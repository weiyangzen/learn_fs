# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zbseq.c

Implements Level 2 binary object sequence support.

Key behavior:
- Defines `names_array_ref_t`, a GC-visible wrapper around a names array ref.
- `create_names_array` allocates system/user name table refs in stable memory and initializes them as readonly empty arrays.
- Initialization installs a fake system name table until PostScript setup installs the real one.
- `.installsystemnames` accepts only a global shortarray at global save level 0, then replaces `system_names_p`.
- `currentobjectformat` and `setobjectformat` expose and mutate the binary object format, accepting only values 0 through 4.
- `.bosobject` encodes one object into binary object-sequence representation using `encode_binary_token`, updating ref/char offsets and returning an 8-byte string slice.

Dependencies and coupling:
- Uses binary-token machinery from `btoken.h`.
- Uses stable/global memory and old-ref assignment to keep name tables GC-safe.
