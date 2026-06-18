# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipfsync/ipsyncm.c

`ipsyncm.c` is a simple one-way IPFilter sync sender. It reads records from `IPSYNC_NAME` and writes them to a connected UDP destination.

Major behaviors:
- Usage is `<destination IP> <destination port>`, defaulting to port `43434`.
- Opens the sync device read-only, creates a UDP socket, connects to the destination, and loops forever with one-second retry sleeps.
- Accumulates reads into a 1400-byte buffer, validates `SYNHDRMAGIC`, waits for complete sync records, then writes the framed record to the UDP socket.
- Has always-on `IPSYNC_DEBUG` printing for header fields, command/table names, sequence number, and TCP update state.

Notes:
- Signal handling code exists but is compiled out with `#if 0`, so normal termination is external process termination.
- Partial reads are handled by moving remaining bytes to the front of the buffer.
- This is more of a debug/legacy utility than the robust daemon in `ipfsyncd.c`.
