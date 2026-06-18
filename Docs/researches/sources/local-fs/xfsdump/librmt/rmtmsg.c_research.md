# File Research: sources/local-fs/xfsdump/librmt/rmtmsg.c

Implements debug/warning message control for `librmt`.

Behavior:
- `RMTDEBUG` environment variable can enable warnings or debug.
- `rmt_turnonmsgs()` enables messages programmatically.
- `_rmt_msg()` prints to stderr when current debug code is high enough.

Risk:
- `_rmt_msg()` uses `vsprintf` into a fixed 256-byte static buffer, so overly long formatted messages can overflow.
