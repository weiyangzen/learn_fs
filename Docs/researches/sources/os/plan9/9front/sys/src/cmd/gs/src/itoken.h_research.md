# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/itoken.h

Declares exported token-related procedures implemented elsewhere, primarily in `ztoken.c`. It includes `ztokenexec_continue` for continuing after procedure-stream refill or callout, and `ztoken_handle_comment` for handling `scan_Comment` or `scan_DSC_Comment` returns from the scanner.

Also declares `ztoken_scanner_options`, which updates cached scanner options in the interpreter context after user parameter changes.
