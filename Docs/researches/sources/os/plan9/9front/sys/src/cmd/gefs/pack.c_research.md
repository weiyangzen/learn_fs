# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/pack.c

gefs serialization and deserialization for keys, values, stats, trees, arenas, and superblocks.

Key responsibilities:
- Packs/unpacks nul-terminated counted strings used in directory keys.
- Converts `Xdir` records to/from B-tree kvps and Plan 9 stat buffers.
- Packs data keys, parent links, labels, snapshot keys, deadlists, block pointers, tree records, arena records, and superblocks.
- Validates superblock magic/version and hash.

Important behavior:
- Directory stat conversion resolves uid/gid/muid through the loaded user table.
- Superblock stores snap root, snap deadlist, arena pointers, flags, next qid/gen, and qgen, followed by a MetroHash checksum.
- `unpacksb()` allocates `fs->arenabp` and restores `fs->qgen`.

Notable risks:
- Many routines assert buffer sizes rather than returning recoverable errors.
- `kv2qid()` reads qid version as 64 bits, although Plan 9 `Qid.vers` is narrower elsewhere.
