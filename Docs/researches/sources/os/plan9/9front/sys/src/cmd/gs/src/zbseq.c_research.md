# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zbseq.c

This file implements Level 2 binary object sequence support.

Key behavior:
- Defines a stable-memory wrapper for the system/user name table reference.
- `create_names_array` allocates a names-array reference in stable memory.
- Initialization creates a temporary fake system name table; PostScript initialization later installs the real one.
- `.installsystemnames` installs the global, readonly shortarray of system names, only from global VM at save level zero.
- `currentobjectformat` and `setobjectformat` expose the binary object format setting.
- `.bosobject` encodes one object into binary object sequence representation using `encode_binary_token`.

Important dependencies:
- Uses binary token machinery from `btoken.h`.
- Uses stable allocator behavior from `gxalloc.h` and `ialloc.h`.
- Registered as Level 2 operators in `zbseq_l2_op_defs`.

Research notes:
- This is serialization/interpreter infrastructure for PostScript binary object sequences, not rendering or filesystem code.
