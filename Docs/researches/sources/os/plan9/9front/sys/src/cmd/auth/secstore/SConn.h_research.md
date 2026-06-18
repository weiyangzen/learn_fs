# File Research: sources/os/plan9/9front/sys/src/cmd/auth/secstore/SConn.h

Header for secstore's delimited authenticated/encrypted connection abstraction.

Key contents:
- Defines `Maxmsg` as 4096.
- Defines `SConn` callback structure: `secret`, `read`, `write`, and `free`.
- Declares `newSConn`, `writerr`, `readstr`, and allocation helpers.
- Documents direction semantics for deriving read/write secrets.

Role:
- Shared interface for secstore client/server PAK and encrypted message exchange.
