# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/cddb.c

This file queries a CDDB/freedb server for album and track metadata.

Key behavior:
- Connects to the configured server on TCP port 888.
- Sends CDDB hello, protocol negotiation, query, and read commands.
- Accepts exact or close matches, using the first returned match.
- Parses `DTITLE` and `TTITLEn` fields and prints title/track listings.
- Can print track durations and total time.

Important details:
- Default server is `freedb.freedb.org`.
- Protocol level 6 is requested for UTF-8.
- Input format is `query diskid ntrack offsets... leadout`.
- Text continuations are appended to existing title strings.

Filesystem relevance:
- Indirect: network metadata utility; no filesystem implementation logic.
