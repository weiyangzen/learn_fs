# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/transport.c

This file implements SSH binary packet construction, parsing helpers, padding, encryption, MAC generation, and packet dumping.

Key behavior:
- Allocates and initializes fixed-buffer `Packet` objects.
- Appends SSH primitive encodings: byte, uint32, string/block, mpint, and raw packet data.
- Extracts SSH strings, uint32s, and mpints.
- `finish_packet` computes SSH padding, packet length, optional HMAC-SHA1, optional encryption, and sequence advancement.
- `undo_packet` decrypts packet bodies, validates HMAC-SHA1, removes padding, and advances input sequence.

Important details:
- Minimum block size is forced to 8 bytes as SSH requires.
- mpint serialization inserts a leading zero when the high bit would make the integer negative.
- MAC input includes sequence number and packet bytes.
- `dump_packet` is a debug hex dump helper.

Filesystem relevance:
- Indirect: transport layer used by the `/net/ssh` filesystem service and client/server helpers.
