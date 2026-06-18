# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/ssh2.h

This small header defines common limits and utility prototypes for the SSH command suite.

Key contents:
- Buffer and path limits including `Maxpayload`, `Maxrpcbuf`, `Copybufsz`, `Blobsz`, `Maxfactotum`, and stack sizes.
- Opaque `Conn` forward declaration for logging signatures.
- Vararg checking pragmas for `esmprint`, `ssdebug`, and `sshlog`.
- Utility prototypes for formatted allocation, logging, pointer freeing, and file reading.

Important details:
- `Maxrpcbuf` is tied to devmnt’s maximum RPC payload.
- `Maxfactotum` bounds reads of `/mnt/factotum/ctl`.

Filesystem relevance:
- Indirect: shared constants shape reads/writes to SSH, factotum, and namespace files.
