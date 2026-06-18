# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libip/ipaux.c

Defines common IP address constants and IPv4/IPv6 conversion helpers.

Key globals:
- `IPv4bcast`, `IPv4allsys`, `IPv4allrouter`, `IPallbits`, `IPnoaddr`, `v4prefix`.

Key functions:
- `isv4`: detects IPv4-mapped IPv6 addresses.
- `v4tov6`: maps a 4-byte IPv4 address to 16-byte IPv4-mapped IPv6 form.
- `v6tov4`: extracts IPv4 bytes from mapped addresses and handles all-zero no-address specially.

Important behavior:
- Conversion code is manually unrolled for speed and to avoid library calls in common paths.
