# File Research: sources/os/plan9/9front/sys/src/cmd/uhtml.c

`uhtml` detects an HTML document’s input character set and converts it to UTF/HTML-safe output through `tcs`. It reads an initial buffer, checks BOMs, scans tags for `encoding=` or `charset=`, and falls back to UTF validation or Latin-1 on rune errors.

With `-p`, it prints the detected charset only. Otherwise it spawns `/bin/rc` running `{tcs -f <charset> || cat} | tcs -f html`, feeds the buffered prefix and remaining stdin through the pipe, and waits.

The attribute parser is simple and tolerant of quoted/unquoted alphanumeric charset values with `-` and `_`.
