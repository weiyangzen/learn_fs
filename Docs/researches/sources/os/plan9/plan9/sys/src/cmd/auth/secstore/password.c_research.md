# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/password.c

Manages secstore account files under `/adm/secstore/who`. `getPW` parses expiration, disabled/STA flags, failed counters, comments, and `PAK-Hi`; it falls back to a `FICTITIOUS` account for nonexistent users to reduce account enumeration.

It rejects expired, disabled, or temporarily locked accounts unless `dead_or_alive` is set. Accounts with at least 10 failures are locked for five minutes based on mtime, then reset.

`putPW` rewrites account metadata and `PAK-Hi`; `freePW` releases all dynamic fields and mpints.
