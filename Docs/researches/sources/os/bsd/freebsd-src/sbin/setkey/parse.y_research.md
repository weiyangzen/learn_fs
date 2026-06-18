# File Research: sources/os/bsd/freebsd-src/sbin/setkey/parse.y

## Summary
Yacc grammar and PF_KEY message builder for `setkey` script input. It parses SAD commands, SPD commands, algorithms, keys, lifetimes, NAT-T options, ESN, hardware offload interface options, address-family flags, ports, and policies.

## Main Responsibilities
- Parses `add`, `delete`, `deleteall`, `get`, `flush`, and `dump` SAD commands.
- Parses `spdadd`, `spddelete`, `spddump`, and `spdflush` SPD commands.
- Parses AH, ESP, IPCOMP, TCP MD5, old AH/ESP syntax, and algorithm/key forms.
- Validates key lengths through `ipsec_check_keylen()`.
- Converts hex and quoted key strings into binary buffers.
- Parses lifetimes, replay windows, reqid, mode, NAT-T endpoints/ports/fragment size, ESN, and hardware offload interface names.
- Parses SPD policy strings through `ipsec_set_policy()`.
- Builds PF_KEY `sadb_msg` buffers with SA, SA2, key, lifetime, address, NAT-T, replay, policy, and hardware-offload extensions.

## Key Elements
- `setkeymsg0()`: initializes base PF_KEY message header.
- `setkeymsg_add()`: builds SADB_ADD messages for source/destination combinations.
- `setkeymsg_addr()`: builds GET/DELETE/DELETEALL messages.
- `setkeymsg_spdaddr()`: builds SPD messages with policy and address extensions.
- `parse_addr()`: resolves addresses with parser-selected family and flags.
- `fix_portstr()`: splits ICMPv6 upper-layer port/type-code syntax.
- `parse_init()`: resets global parser state between commands.

## Dependencies And Integration
Uses PF_KEY v2 structures, FreeBSD netipsec headers, `libpfkey`, `libipsec`, resolver APIs, and tokens supplied by `token.l`.

## Research Notes
The message builders use fixed `BUFSIZ` stack buffers and retain historical comments warning that they do not perform buffer-overrun checks. This is important when analyzing parser robustness.
