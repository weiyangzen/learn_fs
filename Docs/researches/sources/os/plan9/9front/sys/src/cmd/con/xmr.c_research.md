# File Research: sources/os/plan9/9front/sys/src/cmd/con/xmr.c

XMODEM receiver writing fixed 128-byte data blocks to a named output file. It enables raw console mode, sends an initial `Nak`, receives `Soh` blocks, validates sequence/complement/checksum, writes payloads, and acknowledges valid blocks.

Important behavior:
- Handles `Eot` by acknowledging and ending, `Cancel` by aborting.
- `readupto()` tolerates partial reads and supports alarm-based timeouts.
- Invalid blocks trigger resynchronization by searching for the next `Soh`.
- Duplicate previous sequence numbers are acknowledged without rewriting.
- Debug mode dumps resync details to stderr.
