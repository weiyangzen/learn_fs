# File Research: sources/os/plan9/plan9/sys/src/cmd/scuzz/scuzz.c

Interactive Plan 9 SCSI utility.

Key behavior:
- Parses command-line options for raw open, quiet mode, max transfer size, Exabyte quirks, and forced 6-byte commands.
- Opens an optional target device, then reads commands from stdin and dispatches them through a command table.
- Supports general SCSI operations, tape operations, direct read/write/seek/capacity, mode sense/select, CD-R/CD audio commands, changer commands, probe, open, close, and help.
- `read` and `write` can transfer to files or to shell pipelines prefixed with `|`.
- Dumps decoded inquiry, mode pages, TOC, disc info, track info, element status, and sense data.

Important details:
- Uses `Biobuf` for command input and output.
- Maintains a global `rwbuf` up to 240 KiB.
- `probe` scans likely `/dev/sd*` unit names and prints inquiry data.
- Parser supports quoted tokens with doubled single quotes.
- Some old writer commands are present but disabled in the command table.

Filesystem relevance:
- Direct: user-facing tool for Plan 9 `/dev/sdXX` raw SCSI devices, plus file and pipe I/O for device data transfer.
