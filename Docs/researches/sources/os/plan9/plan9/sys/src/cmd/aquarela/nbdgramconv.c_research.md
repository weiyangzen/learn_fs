# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbdgramconv.c

Serializes and parses NetBIOS datagram packets.

Key functions:
- `nbdgramconvM2S` decodes type, flags, id, IPv4 source, source port, and type-specific payload.
- `nbdgramconvS2M` encodes the same structure back to wire format.

Interactions:
- Called by `nbdgram.c` for receive/send paths.
- Uses `nbnameencode` and `nbnamedecode`.

Notable details:
- Direct/group/broadcast datagrams include a length fixup plus source and destination NetBIOS names.
- Error datagrams carry one code byte.
- Query response encode path uses `s->datagram.dstname` where the decode side stores query names in `s->query.dstname`; this is a structure-union sensitivity to watch.
