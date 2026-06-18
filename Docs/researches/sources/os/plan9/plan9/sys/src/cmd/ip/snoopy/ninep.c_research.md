# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ninep.c

`snoopy` 9P message formatter.

Key behavior:
- Uses `convM2S()` to decode a 9P message into `Fcall`.
- Formats decoded message with `%F`.
- Replaces newlines in formatted output with backslashes.
- Falls back to `dump.seprint()` if 9P decode fails.

Integration:
- Reached from TCP/IL/UDP service-port demux entries.

Risks and notes:
- Terminal decoder only; no filtering fields.
