# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ayiya.c

Implements an AYIYA IPv6 tunnel client over UDP with optional shared-secret authentication.

Key points:
- Defines AYIYA header fields, identity/hash/auth/opcode constants, maximum identity/signature/header sizes, and protocol state.
- Supports options:
  - `-d` debug
  - `-g` install global IPv6 route
  - `-m mtu`
  - `-x mtpt` inside network root
  - `-k secret` shared-key authentication seed
- Requires local IPv6/mask, remote UDP endpoint, and remote IPv6.
- `ayiyapack` prepends AYIYA header, identity, timestamp, and signature area before IPv6 payload.
- `ayiyaunpack` decodes AYIYA headers and points identity/signature into the packet.
- `ayiyahash` supports MD5 and SHA1; the configured default uses SHA1 length.
- `ayiyasign` hashes packets with the configured signature placeholder; `ayiyaverify` verifies incoming signature/auth settings.
- `setup` creates a local IPv6 packet interface and optionally adds `2000::/3` route.
- `ip2tunnel` reads IPv6 packets, sends heartbeat packets after read alarms, filters invalid addresses, and forwards with `OpForward`.
- `tunnel2ip` verifies incoming AYIYA packets, handles MOTD/query/echo opcodes, validates forwarded IPv6 payloads, restricts inbound destination to the local subnet, writes to the packet interface, and replies to echo/query as needed.
- `badipv4`/`badipv6` mirror invalid-address filtering from `6in4.c`.

Dependencies and interactions:
- Uses Plan 9 UDP dialing, `ipifc`, `iproute`, `libsec` hashing, alarm/notify, and IP helpers.

Research relevance:
- More complex than `6in4.c`: it demonstrates authenticated tunnel framing, keepalives, control opcodes, and subnet ingress filtering.
