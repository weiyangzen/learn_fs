# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwmainc.c

Purpose: Win32 console launcher for Ghostscript using the DLL/static loader and a separate GUI thread for display windows.

Major responsibilities:
- Bridges Ghostscript stdio to real console stdin/stdout/stderr.
- Starts a secondary Win32 message-loop thread for image windows because the main thread runs Ghostscript and may block on stdin.
- Posts custom display messages to the GUI thread for open/close/size/sync/page/update.
- Uses mutexes to protect image bitmap access across Ghostscript and GUI threads.
- Loads Ghostscript, creates an instance, registers callbacks, injects display defaults, runs Ghostscript, and shuts down the GUI thread.

Key details:
- Custom messages start at `WM_USER+101` to avoid a known Japanese Windows `WM_USER+1` collision.
- Uses `_beginthread` and waits briefly until the GUI thread can receive posted messages.
- Sets stdin to binary when not a TTY and stdout/stderr to binary.
- Display callback structure mirrors `dwmain.c`, but message-passes image work to `winthread`.
- Optional debug memory allocation callbacks are present under `DISPLAY_DEBUG_USE_ALLOC`.

Risks/legacy notes:
- `hthread` is not visibly initialized before the startup wait comparison with `INVALID_HANDLE_VALUE`.
- Uses fixed buffers and older thread/message APIs.
- Pointer debug output uses old integer formatting.

Filesystem relevance: None beyond command-line and console stream behavior.
