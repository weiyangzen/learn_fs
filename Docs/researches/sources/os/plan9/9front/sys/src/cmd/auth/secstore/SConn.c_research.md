# File Research: sources/os/plan9/9front/sys/src/cmd/auth/secstore/SConn.c

Delimited secure connection wrapper used by secstore.

Key responsibilities:
- Wraps an fd in `SConn` with read/write/free/secret callbacks.
- Initially sends and receives SSL-style length-prefixed clear records.
- After `secret`, derives separate in/out RC4 and SHA1 keys from a shared secret and direction.
- Adds SHA1 integrity digest and RC4 encryption to records.
- Tracks per-direction sequence numbers in integrity hashes.
- Provides `writerr` in-band `!message` errors and `readstr` string reads.

Dependencies:
- Uses RC4, HMAC-SHA1/SHA1, Plan 9 fd I/O, and `SConn.h`.

Notable risks:
- This is legacy RC4/SHA1 transport protection.
