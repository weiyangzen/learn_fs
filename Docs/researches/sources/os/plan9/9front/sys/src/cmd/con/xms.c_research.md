# File Research: sources/os/plan9/9front/sys/src/cmd/con/xms.c

XMODEM sender. It opens an input file, enables raw console mode, waits for receiver readiness (`Nak` for checksum or `C` for CRC mode), then sends 128-byte or 1024-byte packets.

Important behavior:
- Options: `-d` debug, `-p` progress, `-1` 1K blocks.
- Builds `Soh` or `Stx` packets with sequence and complement bytes.
- Supports classic additive checksum and CRC-16 via `updcrc()`.
- `send()` retries packets up to 10 times until `Ack`, then reports failure.
- `errorout()` sends `Cancel`, restores raw mode, and exits.
