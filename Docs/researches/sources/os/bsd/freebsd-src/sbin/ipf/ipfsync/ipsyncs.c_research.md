# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipfsync/ipsyncs.c

`ipsyncs.c` is the receiving counterpart to `ipsyncm.c`. It listens on UDP and writes received sync records into `IPSYNC_NAME`.

Major behaviors:
- Usage is `<destination IP> <destination port> [remote IP]`, defaulting to port `43434`.
- Opens `IPSYNC_NAME` write-only, binds a UDP socket with `SO_REUSEADDR`, and loops forever with one-second retry sleeps.
- Reads UDP data into a 1400-byte buffer, validates `SYNHDRMAGIC`, waits for complete records, then writes them to the sync device.
- Prints debug information for command/table/type/sequence and TCP update data.

Important note:
- The source explicitly comments that it does not check the datagram source address, calling this a possible security risk. The optional `remote IP` argument is parsed into `in.sin_addr`, but not actually used for validation in the receive loop.

Like `ipsyncm.c`, signal handling is disabled under `#if 0`, and the code appears intended for testing or simple deployments rather than hardened operation.
