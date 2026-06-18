# File Research: sources/os/plan9/plan9/sys/src/cmd/aan.c

`aan` is an always-available network relay for preserving a byte stream, commonly a 9P connection, across disconnect/reconnect events.

Key responsibilities:
- Runs in client or server mode over a dial string or network directory.
- Wraps payload chunks in a 12-byte little-endian header containing byte count, message number, and acked count.
- Buffers unsent and unacknowledged messages through Plan 9 thread channels.
- Runs separate client-reader, network-reader, and timer processes.
- Periodically sends synchronization/ack-only messages.
- Reconnects automatically and retransmits unacknowledged messages.
- Reads endpoint metadata from Plan 9 network connection directories for logging.
- Exits on client EOF or server-side listen timeout.

Dependencies:
- Uses Plan 9 threads, channels, `Alt`, `dial`, `listen`, `accept`, `/net` endpoint files, `readn`, `syslog`, and `fcallfmt`.

Notable risks:
- Fixed 8 KiB payload buffers and 10-buffer channel pools bound in-flight data.
- Header packing is explicitly little-endian.
- Message counters are `ulong`/`int` style and can wrap on long sessions.
