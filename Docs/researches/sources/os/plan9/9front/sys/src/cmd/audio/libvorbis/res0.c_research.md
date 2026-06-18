# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/res0.c

Implementation of Vorbis residue backends 0, 1, and 2.

Important routines:
- `res0_free_info()` and `res0_free_look()` release residue setup/lookups.
- `res0_pack()` serializes residue setup fields and second-stage cascades.
- `res0_unpack()` parses residue setup, validates book indexes/maptypes, and checks phrasebook partition geometry.
- `res0_look()` builds runtime partbook pointers and decode maps.
- `local_book_besterror()` selects nearest encode codebook entry for integer vectors.
- `_01class()` and `_2class()` classify residue partitions for type 0/1 and type 2 coding.
- `_01forward()` encodes partition words and residue values.
- `_01inverse()` decodes type 0/1 residue data.
- `res0_inverse()`, `res1_*()`, and `res2_*()` expose backend-specific encode/decode behavior.
- `residue0_exportbundle`, `residue1_exportbundle`, and `residue2_exportbundle` register backend hooks.

Integration points:
- Uses `codebook.c` decode/encode APIs and setup from `codec_internal.h`.
- Called via `_residue_P` registry from mapping backends.
- Training/debug code can emit `.vqd` files when compile-time flags are enabled.

Risk and review signals:
- Decode treats truncated packets as “stop working” and returns success-like `0`, matching libvorbis robustness behavior.
- Setup unpack has important range checks for codebook indexes and phrasebook sizing.
- Several allocation paths do not explicitly handle allocation failure.
- Type 2 interleaves channels into one vector, so channel count and `pcmend` arithmetic are security-sensitive.

Filesystem relevance:
- No filesystem logic. Optional training modes write files, but normal code is audio bitstream residue coding.
