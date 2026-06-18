# File Research: sources/local-fs/reiserfsprogs/debugreiserfs/pack.c

Implements `debugreiserfs -p` metadata packing.

Pack stream layout:
- ReiserFS magic.
- Block size.
- Packed superblock, bitmap blocks, journal blocks.
- Remaining selected metadata blocks.
- End magic.

Packing strategy:
- Leaves are compacted item-by-item when structurally valid.
- Suspicious/corrupt leaves, internal nodes, superblock, bitmap blocks, journal blocks, and unknown blocks requested as mandatory are emitted as full blocks.
- Blocks are cleared from `what_to_pack` after serialization to avoid duplicates.

Leaf item packing:
- Common key fields are omitted when inferable from prior item.
- Offsets may be omitted, stored as 32-bit, or stored as 64-bit.
- Direct items generally omit contents and are later reconstructed as filler, except safe links.
- Indirect items may be serialized whole or compressed as extents/runs.
- Directory items serialize entries, names, object ids, and optional dirid/generation/state.
- Stat data serializes compact old/new stat-data fields.

Journal support:
- Packs internal/default journal from filesystem journal area.
- Supports separated journal markers when a non-standard journal device is supplied.
- Warns and requires confirmation if a separate journal exists but was not specified.

Global counters report compressed leaves, full blocks, bad leaves, internals, and compression ratio.

Notable risks/quirks:
- Internal-node compact packing is stubbed; internals are always full-block packed.
- `descs` and `others` counters are declared but not meaningfully populated.
- Compact direct-item reconstruction loses real file data by design.
