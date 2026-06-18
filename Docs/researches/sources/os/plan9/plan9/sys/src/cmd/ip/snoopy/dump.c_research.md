# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/dump.c

Fallback `snoopy` payload formatter.

Key behavior:
- Prints up to `Nflag` bytes.
- Chooses escaped printable text if all bytes are printable/space, otherwise hex.
- Terminates protocol walk.

Integration:
- Used as default demux target for unknown protocols and payload tails.

Risks and notes:
- Leaves `m->ps` unchanged while setting `m->pr=nil`; this is fine for terminal formatting.
