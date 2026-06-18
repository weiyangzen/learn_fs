# File Research: sources/os/plan9/plan9/sys/src/cmd/con/xms.c

XMODEM sender for a named file.

It waits up to 30 seconds for receiver readiness (`NAK` for checksum mode or `C` for CRC mode), sends 128-byte `SOH` blocks by default or 1024-byte `STX` blocks with `-1`, pads the final block with zero bytes, and retries each block until ACK or failure. It supports `-d` debug output and `-p` progress messages.

CRC mode uses a local CRC-CCITT update function. On repeated failure it sends `Cancel`, restores console raw mode, and exits with an error.
