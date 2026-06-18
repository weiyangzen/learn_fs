# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/aoerr.c

`snoopy` decoder for AoE error/list style payloads.

Key behavior:
- Parses command and Ethernet-address count.
- Filters on command, count, or contained Ethernet address.
- Formats command name, count, and up to several Ethernet addresses.

Integration:
- Selected by `aoe.c` command demux value `3`.

Risks and notes:
- Field table maps `"ea"` to `Onea` instead of `Oea`, so Ethernet-address filtering is unreachable.
- Printing loop uses `m->pe + 6*i` instead of `m->ps + 6*i`, likely invalid output.
- Loop condition `if(h->nea < i)` should likely be `i >= h->nea`.
