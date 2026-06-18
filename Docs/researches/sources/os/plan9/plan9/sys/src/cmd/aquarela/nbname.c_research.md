# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbname.c

NetBIOS name encoding/decoding, formatting, local-name table, and remote-name cache.

Key functions:
- `nbnamedecode` and `_nameextract` parse RFC-style compressed NetBIOS names from NBNS packets.
- `nbnameencode` writes the 32-character encoded NetBIOS name plus terminator.
- `nbmknamefromstring`, `nbmknamefromstringandtype`, and `nbmkstringfromname` convert between readable names and fixed 16-byte names.
- `nbnameequal` supports wildcard matching through `*`.
- `nbnametablefind` tracks locally listened/owned names.
- `nbremotenametablefind` and `nbremotenametableadd` implement a TTL-based remote name cache.

Interactions:
- Shared by NBNS, datagram, session, and browse code.
- Installs with `%B` formatter via `nbnamefmt`.

Notable details:
- Name type is stored in byte 15 and may be specified as `\xNN`.
- `_nameextract` handles compression pointers recursively.
