# File Research: sources/os/plan9/plan9/sys/src/cmd/srvold9p/fcall.c

Stream reassembler for old 9P1 messages.

Key responsibilities:
- Determines complete 9P1 message lengths from byte streams.
- Handles variable-length `Twrite9p1` and `Rread9p1` by reading count fields.
- Forks a process that reads from an old service fd, reassembles complete messages, and writes them to a pipe.

Important functions:
- `mntrpclen`: returns complete message length when enough bytes are buffered, zero otherwise.
- `fcall`: creates pipe, forks reassembler, and returns read end to caller.

Use case:
- Interposed for stream transports where old 9P1 messages may arrive fragmented or coalesced.

Risks/quirks:
- Illegal/unknown fixed-length message types are consumed as available bytes.
- Child closes fds 0..19 except needed descriptors.
