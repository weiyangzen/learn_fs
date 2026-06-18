# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/SConn.h

Declares `SConn`, `Maxmsg`, secure-connection callbacks, constructor, in-band error helpers, and memory helper prototypes.

Documents that `secret(conn, bytes, dir)` derives direction-specific digest/encryption keys, with `dir=0` for client and `dir=1` for server.
