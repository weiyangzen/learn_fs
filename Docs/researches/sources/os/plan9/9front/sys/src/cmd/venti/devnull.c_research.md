# File Research: sources/os/plan9/9front/sys/src/cmd/venti/devnull.c

Purpose: Minimal Venti server that accepts writes and discards data.

Key behavior:
- Listens on an address, defaulting to `tcp!*!venti`.
- Responds to ping, goodbye, write, and sync.
- For writes, returns the packet SHA1 score without storing data.
- For reads, returns a `no such block` error.
- Optional verbose request/response logging.

Dependencies:
- Uses Venti server request APIs, threading, packet SHA1, and Venti formatters.

Notable details:
- Useful for testing write clients without persistent storage.
