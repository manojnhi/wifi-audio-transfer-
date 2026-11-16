"""Simple Windows desktop controller for the Sound Transfer WiFi server."""

from __future__ import annotations

import os
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

import app as audio_server


class SoundTransferDesktop:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.process: subprocess.Popen | None = None
        self.log_path: Path | None = None
        self.root.title("Sound Transfer WiFi")
        self.root.geometry("520x380")
        self.root.minsize(440, 340)
        self.root.configure(bg="#10151c")
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        tk.Label(root, text="Sound Transfer WiFi", font=("Segoe UI", 22, "bold"),
                 fg="#f4f7fb", bg="#10151c").pack(pady=(26, 8))
        tk.Label(root, text="Computer audio ko phone par same Wi-Fi se sunen",
                 font=("Segoe UI", 11), fg="#b9c9d6", bg="#10151c").pack(pady=(0, 20))

        self.start_button = tk.Button(root, text="Start computer server", command=self.start,
                                      font=("Segoe UI", 12, "bold"), bg="#41d6a4", fg="#071b15",
                                      activebackground="#33bd90", relief="flat", padx=16, pady=10)
        self.start_button.pack(pady=6)

        self.status = tk.Label(root, text="Server is stopped", font=("Segoe UI", 10),
                               fg="#b9c9d6", bg="#10151c")
        self.status.pack(pady=(14, 4))
        self.address = tk.StringVar(value="")
        self.address_entry = tk.Entry(root, textvariable=self.address, justify="center",
                                      font=("Segoe UI", 13), state="readonly", readonlybackground="#202b36",
                                      fg="#ffffff", relief="flat", width=36)
        self.address_entry.pack(pady=8, ipady=9)
        self.copy_button = tk.Button(root, text="Copy address", command=self.copy_address,
                                     font=("Segoe UI", 10), bg="#293846", fg="#ffffff",
                                     activebackground="#35495a", relief="flat", padx=14, pady=7,
                                     state="disabled")
        self.copy_button.pack(pady=4)
        tk.Label(root, text="Phone aur computer ko ek hi Wi-Fi par rakhein.\n"
                           "Phone app mein upar wala address daal kar Connect karein.\n"
                           "Firewall pooche to Python/app ko Private network par allow karein.",
                 font=("Segoe UI", 9), fg="#aebdca", bg="#10151c", justify="center").pack(pady=(18, 8))

    def start(self) -> None:
        if self.process and self.process.poll() is None:
            return
        if getattr(sys, "frozen", False):
            command = [sys.executable, "--server"]
        else:
            command = [sys.executable, str(Path(__file__).resolve()), "--server"]
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            log_dir = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Sound Transfer WiFi"
            log_dir.mkdir(parents=True, exist_ok=True)
            self.log_path = log_dir / "server.log"
            log_file = self.log_path.open("ab", buffering=0)
            self.process = subprocess.Popen(command, stdin=subprocess.DEVNULL,
                                             stdout=log_file, stderr=subprocess.STDOUT,
                                             creationflags=creationflags,
                                             close_fds=(os.name != "nt"))
            log_file.close()
        except OSError as exc:
            messagebox.showerror("Could not start server", str(exc), parent=self.root)
            return
        self.address.set(f"http://{audio_server.local_ip()}:{audio_server.PORT}")
        self.status.config(text="Server is running. Keep this app open.", fg="#41d6a4")
        self.start_button.config(text="Stop computer server", command=self.stop, bg="#e28b73")
        self.copy_button.config(state="normal")
        self.root.after(1000, self.check_server)

    def check_server(self) -> None:
        if self.process and self.process.poll() is not None:
            self.process = None
            self.address.set("")
            log_hint = f" Details: {self.log_path}" if self.log_path else ""
            self.status.config(text="Server stopped. Check the log file." + log_hint, fg="#ff7979", wraplength=440)
            self.start_button.config(text="Start computer server", command=self.start, bg="#41d6a4")
            self.copy_button.config(state="disabled")
            return
        if self.process:
            self.root.after(1000, self.check_server)

    def copy_address(self) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append(self.address.get())
        self.status.config(text="Address copied. Enter it in the phone app.", fg="#41d6a4")

    def stop(self) -> None:
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.process = None
        self.address.set("")
        self.status.config(text="Server is stopped", fg="#b9c9d6")
        self.start_button.config(text="Start computer server", command=self.start, bg="#41d6a4")
        self.copy_button.config(state="disabled")

    def close(self) -> None:
        self.stop()
        self.root.destroy()


if __name__ == "__main__" and "--server" in sys.argv:
    audio_server.main()
elif __name__ == "__main__":
    window = tk.Tk()
    SoundTransferDesktop(window)
    window.mainloop()
