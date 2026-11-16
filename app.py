"""Stream Windows system audio to browsers on the same Wi-Fi network."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import socket
import threading
from pathlib import Path

import numpy as np
import soundcard as sc
from aiohttp import web

HOST = "0.0.0.0"
PORT = 8765
SAMPLE_RATE = 44_100
CHUNK_FRAMES = 2_205  # 50 ms
PAGE = Path(__file__).with_name("index.html")
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def local_ip() -> str:
    """Find the IPv4 address used to reach the local network."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("192.0.2.1", 80))  # TEST-NET address; no packet is sent.
        return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()


class AudioBroadcaster:
    def __init__(self) -> None:
        self.clients: set[web.WebSocketResponse] = set()
        self.loop: asyncio.AbstractEventLoop | None = None
        self.thread: threading.Thread | None = None
        self.stop_event = threading.Event()

    async def add(self, ws: web.WebSocketResponse) -> None:
        self.clients.add(ws)
        if self.thread is None or not self.thread.is_alive():
            self.stop_event.clear()
            self.thread = threading.Thread(target=self._capture, daemon=True)
            self.thread.start()

    async def remove(self, ws: web.WebSocketResponse) -> None:
        self.clients.discard(ws)
        if not self.clients:
            self.stop_event.set()

    def _capture(self) -> None:
        try:
            speaker = sc.default_speaker()
            if speaker is None:
                raise RuntimeError("No default Windows playback device was found.")
            loopback = sc.get_microphone(id=str(speaker.name), include_loopback=True)
            logging.info("Capturing playback device: %s", speaker.name)
            with loopback.recorder(samplerate=SAMPLE_RATE, channels=2, blocksize=CHUNK_FRAMES) as recorder:
                while not self.stop_event.is_set():
                    samples = recorder.record(numframes=CHUNK_FRAMES)
                    # Average stereo to mono and send little-endian float32 PCM.
                    mono = np.asarray(samples, dtype="<f4").mean(axis=1).astype("<f4", copy=False)
                    if self.loop is not None:
                        asyncio.run_coroutine_threadsafe(self._broadcast(mono.tobytes()), self.loop)
        except Exception as exc:  # Surface device errors in the server log.
            logging.exception("Audio capture stopped: %s", exc)

    async def _broadcast(self, payload: bytes) -> None:
        stale = []
        for ws in tuple(self.clients):
            if ws.closed:
                stale.append(ws)
                continue
            try:
                await ws.send_bytes(payload)
            except (ConnectionError, RuntimeError):
                stale.append(ws)
        for ws in stale:
            self.clients.discard(ws)


broadcaster = AudioBroadcaster()


async def home(_request: web.Request) -> web.FileResponse:
    return web.FileResponse(PAGE)


async def stream(request: web.Request) -> web.WebSocketResponse:
    ws = web.WebSocketResponse(heartbeat=20, max_msg_size=0)
    await ws.prepare(request)
    broadcaster.loop = asyncio.get_running_loop()
    await broadcaster.add(ws)
    logging.info("Listener connected from %s", request.remote)
    try:
        async for message in ws:
            if message.type == web.WSMsgType.ERROR:
                logging.warning("WebSocket error: %s", ws.exception())
    finally:
        await broadcaster.remove(ws)
        logging.info("Listener disconnected")
    return ws


async def on_shutdown(_app: web.Application) -> None:
    broadcaster.stop_event.set()
    if broadcaster.thread and broadcaster.thread.is_alive():
        await asyncio.to_thread(broadcaster.thread.join, 2)


def main() -> None:
    if not PAGE.exists():
        raise SystemExit("index.html is missing from the project folder.")
    app = web.Application()
    app.router.add_get("/", home)
    app.router.add_get("/stream", stream)
    app.on_shutdown.append(on_shutdown)
    address = local_ip()
    print(f"\nSound Transfer WiFi is ready. On your phone, open: http://{address}:{PORT}")
    print("Keep this window open. Press Ctrl+C to stop.\n")
    with contextlib.suppress(KeyboardInterrupt):
        web.run_app(app, host=HOST, port=PORT, print=None)


if __name__ == "__main__":
    main()
