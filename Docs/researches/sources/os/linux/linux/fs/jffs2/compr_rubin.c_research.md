# File Research: sources/os/linux/linux/fs/jffs2/compr_rubin.c

This file implements Rubin arithmetic-style bit compression and decompression for legacy JFFS2 formats. It defines bitstream helpers (`pushpull`), arithmetic codec state (`rubin_state`), MIPS-tuned static probabilities, and dynamic probability encoding.

Core bitstream helpers are `init_pushpull()`, `pushbit()`, `pullbit()`, and `pushedbits()`. Codec helpers include `init_rubin()`, `encode()`, `end_rubin()`, `init_decode()`, `__do_decode()`, and `decode()`. `out_byte()` encodes eight bits of a byte using per-bit probabilities; `in_byte()` decodes the inverse.

`rubin_do_compress()` encodes input bytes into a bounded destination bitstream and fails if compressed size is not smaller than consumed input. The old `jffs2_rubinmips_compress()` is compiled out. `jffs2_dynrubin_compress()` builds an input histogram, derives eight dynamic probability bytes, stores them as an 8-byte header, then compresses the payload with divider 256.

`rubin_do_decompress()` reconstructs bytes until `destlen` is produced. `jffs2_rubinmips_decompress()` uses static MIPS probabilities. `jffs2_dynrubin_decompress()` reads the 8-byte probability header and decodes the remaining stream.

The two compressor descriptors are intentionally legacy-oriented. `rubinmips` has no compress callback and is decompression-only. `dynrubin` has a compressor implementation but is disabled by default via `JFFS2_DYNRUBIN_DISABLED`. Note the on-flash IDs in the descriptors are historically confusing: names and `JFFS2_COMPR_*` constants are cross-assigned for compatibility.

Key dependencies: `compr.h`, legacy on-flash compression IDs, and the compressor registry.
