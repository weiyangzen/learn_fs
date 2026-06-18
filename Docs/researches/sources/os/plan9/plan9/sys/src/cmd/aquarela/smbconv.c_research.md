# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbconv.c

Little-endian SMB integer conversion helpers.

Key functions:
- `smbnhgets`, `smbnhgetl`, `smbnhgetv` read 16-, 32-, and 64-bit little-endian values.
- `smbhnputs`, `smbhnputl`, `smbhnputv` write 16-, 32-, and 64-bit little-endian values.

Interactions:
- Used by SMB buffer/header/command parsing and construction.

Notable details:
- Separate from Plan 9 network-order helpers because SMB fields are little-endian.
