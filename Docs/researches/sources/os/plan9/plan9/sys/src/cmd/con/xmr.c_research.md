# File Research: sources/os/plan9/plan9/sys/src/cmd/con/xmr.c

XMODEM receiver writing received 128-byte blocks to a named file.

It enables raw console mode, sends initial `NAK`, reads packets framed by `SOH`, sequence number, inverse sequence number, 128 data bytes, and checksum, resynchronizes on bad packets, ACKs duplicate previous packets, writes expected packets, and stops on `EOT`. `Cancel` aborts the transfer, and `alarm` notifications implement receive timeouts.

The implementation supports checksum XMODEM only; it does not receive 1K or CRC-mode blocks.
