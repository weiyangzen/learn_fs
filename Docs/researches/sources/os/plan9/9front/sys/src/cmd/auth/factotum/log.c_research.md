# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/log.c

Factotum in-memory log buffer and blocking log-read support.

Key responsibilities:
- Maintains a 128-message ring buffer.
- Queues 9P read requests until log messages are available.
- Flushes/interupts queued reads.
- Truncates long messages safely, avoiding splitting UTF-8 continuation bytes.
- Mirrors messages to stderr when factotum debug mode is enabled.
- Provides `flog` formatted logging.

Dependencies:
- Uses factotum `Logbuf`, lib9p `Req`, locks, and `estrdup9p`.

Notable risks:
- Old messages are dropped by overwriting ring slots when the write pointer wraps.
