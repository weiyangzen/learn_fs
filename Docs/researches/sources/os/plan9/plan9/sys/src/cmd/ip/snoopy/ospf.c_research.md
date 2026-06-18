# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ospf.c

`snoopy` OSPF packet formatter.

Key behavior:
- Parses OSPF common header and prints version, type, length, router, area, checksum, and authentication summary.
- Formats hello packets, database-description LSA headers, link-state updates, and link-state acknowledgments.
- Includes structures for router, network, summary, and AS-external LSAs.
- Falls back to hex dump for unsupported or unexpected payloads.

Integration:
- Reached from IPv4/IPv6 protocol number 89.

Risks and notes:
- No filter/compile callbacks.
- Length validation appears inverted: if OSPF header length is less than captured length, it returns short/error rather than truncating extra bytes.
