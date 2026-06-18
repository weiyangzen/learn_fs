# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/conv.c

Defines packed on-disk format conversion for arena partitions, arenas, clumps, index sections, index entries, buckets, and Bloom headers.

Key behavior:
- Uses explicit big-endian `U8/U16/U32/U64` get/put macros.
- `unpack/packarenapart` handle arena partition superblock.
- `unpackarena` and `_packarena` handle arena trailer formats v4/v5 plus v5a extension fields for `memstats`.
- `unpackarenahead` and `packarenahead` handle redundant arena header.
- `unpackclump`/`packclump` and `unpackclumpinfo`/`packclumpinfo` handle clump metadata.
- `unpackisect`/`packisect` handle index-section headers v1/v2 and optional bucket magic.
- `unpackientry`/`packientry` handle packed index entries.
- `unpackibucket`/`packibucket` handle bucket entry count and bucket magic.
- `unpackbloomhead`/`packbloomhead` handle Bloom metadata.

Compatibility details:
- Arena v4 loses custom clump magic and uses `_ClumpMagic`.
- Arena memstats extension is omitted when equal to diskstats; pack clears old extension bytes to avoid stale fields.
- Unpack has a specific compatibility fix for sealed diskstats with stale unsealed memstats.

Notable issues:
- `unpackientry` contains a debug print when the high byte of `ia.addr` is nonzero.
- Conversion functions `sysfatal` on internal size mismatches, making packed-size definitions critical.
