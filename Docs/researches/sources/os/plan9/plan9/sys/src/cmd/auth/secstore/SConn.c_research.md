# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/SConn.c

Implements secstore’s framed secure connection abstraction. Before session secret setup, records are length-prefixed plaintext. After `SC_secret`, records include SHA1 integrity over secret, plaintext, and sequence number, then RC4 encryption over digest and payload.

`newSConn` wraps an fd and installs read/write/free/secret methods. `readstr` implements secstore’s in-band error convention where messages starting with `!` become errors; `writerr` sends such error messages.

This is the full version used by secstore commands and daemon, while factotum embeds a local copy.
