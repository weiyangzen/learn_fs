# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/win32.c

This file is the Windows host runtime shim for drawterm.

Key behavior:
- Implements `_getproc`/`_setproc` using Windows TLS.
- `osinit`, `osnewproc`, `osproc`, `tramp`, `procsleep`, and `procwakeup` map hosted `Proc` execution to Windows threads/events.
- Provides random data through CryptoAPI in `random20`/`randominit`.
- Provides `seconds`, `ticks`, `fastticks`, sleep/yield, and Windows error-string conversion.
- `WinMain` converts the Windows command line to UTF-8 argv and calls `main`.

Important details:
- Includes UTF-16/Rune conversion helpers `wstrutflen`, `wstrtoutf`, `wstrlen`, and Unicode capability detection.
- `osrerrstr` formats `GetLastError` messages and maps Winsock errors.
- Console argv parsing handles quotes and whitespace manually.
