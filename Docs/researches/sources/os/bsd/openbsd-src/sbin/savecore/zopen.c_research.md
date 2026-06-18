# File Research: sources/os/bsd/openbsd-src/sbin/savecore/zopen.c

This file implements a `funopen()`-backed `.Z` LZW compressor stream for `savecore`.

Key APIs:
- `zopen()`: opens a file and returns a writable `FILE *` whose writes are compressed.
- `z_open()`: allocates and initializes `struct s_zstate`.
- `zwrite()`: compresses input bytes using classic LZW with block compression and variable-width codes.
- `z_close()` / internal `zclose()`: writes final code/EOF bits, closes the fd, and optionally fills `z_info`.
- `output()`: packs variable-width codes into the output byte buffer.
- `cl_block()`, `cl_hash()`: adaptive table-clear logic and hash reset.

Behavior and integration:
- Emits classic compress magic bytes `0x1f 0x9d` and a 16-bit max-code header by default.
- Uses open-addressed hash tables for prefix+character combinations.
- Supports write mode in the local `zopen()` wrapper; read-side state members exist but local `funopen()` does not install a read callback.
- Called by `savecore.c` only for writing compressed kernel/core files.

Risk notes:
- This is legacy compression code with large in-memory tables and bit-packing logic.
- `zopen()` creates files with `O_WRONLY|O_CREAT` but not `O_TRUNC`; callers that expect truncation depend on new paths or prior cleanup.
- Some read/decompression declarations in `compress.h` are not implemented here.
