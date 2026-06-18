# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/lib/netcheck.c

Implements network challenge-response helpers for Securenet/netkey. `netresp` encrypts the ASCII decimal challenge with the DES key and formats the high 32 bits as hex. `netdecimal` maps hex letters to keypad-style decimal digits.

`netcheck` accepts either the hex response or decimal-mapped response, after first trying `smartcheck`. `smartcheck` implements a checksum-like variant that transforms challenge digits, encrypts them, and compares decimalized bytes.

Also provides `checksum`, a key verification checksum formatted as `C xx...`.
