# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/xml.c

Purpose: Emits XML fragments for Venti arena/index metadata.

Key behavior:
- `xmlarena` writes an empty element with arena name, version, partition, block size, start/stop, created/modified times, sealed state, score, clump counts, and storage/data sizes.
- `xmlindex` writes index metadata and nested sections, arena maps, and arenas.
- `xmlamap` writes a map entry with name/start/stop.

Dependencies:
- Uses `Hio`, Venti index/arena structures, XML helper functions declared in `xml.h`, and clump size constants.

Notable details:
- Other XML scalar escaping/formatting helpers are declared in the header but implemented elsewhere.
