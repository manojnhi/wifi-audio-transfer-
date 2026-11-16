package com.soundtransfer.wifi

import android.app.Activity
import android.graphics.Color
import android.os.Bundle
import android.view.View
import android.view.inputmethod.EditorInfo
import android.webkit.WebChromeClient
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView

class MainActivity : Activity() {
    private lateinit var address: EditText
    private lateinit var webView: WebView
    private lateinit var connectButton: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.statusBarColor = Color.rgb(16, 21, 28)
        window.navigationBarColor = Color.rgb(16, 21, 28)

        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(18), dp(18), dp(18), dp(12))
            setBackgroundColor(Color.rgb(16, 21, 28))
        }
        val title = TextView(this).apply {
            text = "Sound Transfer WiFi"
            textSize = 22f
            setTextColor(Color.WHITE)
            setPadding(0, 0, 0, dp(10))
        }
        val instructions = TextView(this).apply {
            text = "Computer par server chala kar uska address daalein, jaise http://192.168.1.23:8765"
            textSize = 14f
            setTextColor(Color.LTGRAY)
            setPadding(0, 0, 0, dp(12))
        }
        address = EditText(this).apply {
            hint = "http://computer-ka-IP:8765"
            setSingleLine(true)
            inputType = android.text.InputType.TYPE_CLASS_TEXT or android.text.InputType.TYPE_TEXT_VARIATION_URI
            imeOptions = EditorInfo.IME_ACTION_GO
            setTextColor(Color.WHITE)
            setHintTextColor(Color.GRAY)
            setPadding(dp(12), dp(10), dp(12), dp(10))
            setBackgroundColor(Color.rgb(35, 45, 56))
        }
        connectButton = Button(this).apply {
            text = "Connect to computer"
            setOnClickListener { connect() }
        }
        webView = WebView(this).apply {
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.mediaPlaybackRequiresUserGesture = true
            webViewClient = WebViewClient()
            webChromeClient = WebChromeClient()
            setBackgroundColor(Color.rgb(16, 21, 28))
        }
        address.setOnEditorActionListener { _, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_GO) { connect(); true } else false
        }
        root.addView(title)
        root.addView(instructions)
        root.addView(address, LinearLayout.LayoutParams(-1, dp(52)))
        root.addView(connectButton, LinearLayout.LayoutParams(-1, dp(54)))
        root.addView(webView, LinearLayout.LayoutParams(-1, 0, 1f))
        setContentView(root)
    }

    private fun connect() {
        var url = address.text.toString().trim()
        if (url.isBlank()) {
            address.error = "Computer ka address daalein"
            return
        }
        if (!url.startsWith("http://") && !url.startsWith("https://")) url = "http://$url"
        val authority = url.substringAfter("://").substringBefore('/')
        if (!authority.contains(':')) {
            url = url.trimEnd('/') + ":8765"
        }
        address.setText(url)
        connectButton.visibility = View.GONE
        address.visibility = View.GONE
        webView.loadUrl(url)
    }

    private fun dp(value: Int): Int = (value * resources.displayMetrics.density).toInt()

    @Deprecated("Deprecated in Android API")
    override fun onBackPressed() {
        if (::webView.isInitialized && webView.canGoBack()) webView.goBack() else super.onBackPressed()
    }

    override fun onDestroy() {
        if (::webView.isInitialized) webView.destroy()
        super.onDestroy()
    }
}
