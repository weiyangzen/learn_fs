# File Research: sources/os/plan9/9front/sys/src/cmd/gs/icclib/icc.h

Primary public header for Graeme Gill's `icclib` ICC profile library.

Key points:
- Defines platform-sized signed/unsigned integer aliases (`INR8/16/32`, `ORD8/16/32`) and includes `icc9809.h`, which supplies the raw ICC.1:1998-09 on-disk constants and structures.
- Provides object-like C interfaces with function pointers for file access (`icmFile`), standard-file backing (`icmFileStd`), memory-image backing (`icmFileMem`), heap allocation (`icmAlloc`), and the top-level `icc` profile object.
- Uses `ICM_BASE_MEMBERS` as a common tag-object method layout: tag type, owning profile pointer, touched/refcount bookkeeping, size/read/write/delete methods, dump, and allocate.
- Defines in-memory/native forms of ICC tag data: numeric arrays, `icmXYZNumber`, response curves, transfer curves with reverse lookup cache (`icmRevTable`), data/text/date tags, LUTs, measurements, named colors, text descriptions, profile sequence descriptions, screening, UCR/BG, viewing conditions, CRD info, and Apple/ColorSync video-card gamma.
- Defines `icmLut` and lookup object families (`icmLuMono`, `icmLuMatrix`, `icmLuLut`) with component operations for curves, matrices, CLUT interpolation, normalization/denormalization, absolute/relative conversion, and range/query helpers.
- The top-level `icc` object exposes profile lifecycle and tag-table APIs: `get_size`, `read`, `write`, `dump`, `del`, `find_tag`, `read_tag`, `add_tag`, `rename_tag`, `link_tag`, `unread_tag`, `read_all_tags`, `delete_tag`, and `get_luobj`.
- Public utilities include signature/string conversion, enum description, XYZ/Lab conversion, standard illuminants (`icmD50`, `icmD65`, `icmBlack`), pseudo-Hilbert grid iteration, chromatic adaptation matrix generation, and Delta-E helpers.

Dependencies and interactions:
- Depends on standard C headers plus `icc9809.h`.
- Implementations are expected in the surrounding icclib C files; this header establishes the ABI-style contract used by Ghostscript color-management code.
- `new_icc()` and `new_icc_a()` create profile objects with default or caller-supplied allocators; all object internals route through the allocator and file abstractions declared here.

Risk notes:
- Assumes native machine sizes compatible with the typedef defaults unless callers override `INR*`/`ORD*`; this matters on platforms where `long` is not 32 bits.
- The API is pointer-heavy and manually reference-counted for tag sharing, so callers must respect `unread_tag`, `delete_tag`, object `del`, and allocator ownership rules.
- `MAX_CHAN` is 15, and LUT helper arrays include `1 << MAX_CHAN` entries; malformed profiles or unsupported channel counts need validation in implementation code.
