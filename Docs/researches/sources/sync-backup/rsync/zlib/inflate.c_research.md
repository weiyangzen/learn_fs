# sources/sync-backup/rsync/zlib/inflate.c

Purpose: main zlib decompressor implementation. It parses zlib, gzip, or raw deflate streams, builds dynamic Huffman tables, decodes stored/fixed/dynamic blocks, maintains the sliding window, validates trailers, supports dictionaries, sync recovery, header extraction, copying, and reset/end operations.

Important APIs and functions: public entry points include `inflateInit_`, `inflateInit2_`, `inflate`, `inflateEnd`, `inflateReset`, `inflateReset2`, `inflateResetKeep`, `inflatePrime`, `inflateSetDictionary`, `inflateGetDictionary`, `inflateGetHeader`, `inflateSync`, `inflateSyncPoint`, `inflateCopy`, `inflateUndermine`, and `inflateMark`. Internal helpers are `fixedtables`, `updatewindow`, optional `makefixed`, and `syncsearch`. Macros such as `LOAD`, `RESTORE`, `PULLBYTE`, `NEEDBITS`, `BITS`, `DROPBITS`, and `BYTEBITS` implement the resumable bit accumulator.

Control flow: `inflate()` is a large resumable state machine over `inflate_mode`. It starts in `HEAD`, accepts raw/zlib/gzip headers, optionally records gzip metadata, requests preset dictionaries, reads block type bits, handles stored blocks, builds dynamic code tables through `inflate_table`, decodes literals and matches, delegates to `inflate_fast` when buffers are large enough, validates checksum/length trailers, and returns `Z_STREAM_END`, `Z_OK`, `Z_BUF_ERROR`, or an error. `goto inf_leave` centralizes counter updates, checksum updates, window maintenance, and progress-based return selection.

State and persistence: persistent state is `struct inflate_state` allocated in `inflateInit2_`. It stores mode, wrapper flags, checksum, gzip header target, window allocation and cursors, bit accumulator, current length/distance, dynamic table scratch arrays, decode tables, and diagnostic mark fields. `updatewindow` lazily allocates the circular window only when back-references across calls require it or a dictionary is installed.

Dependencies and integration points: includes `zutil.h`, `inftrees.h`, `inflate.h`, and `inffast.h`. Uses `adler32`, `crc32`, `ZSWAP32`, `ZALLOC`/`ZFREE`, and decode tables from `inftrees.c`/`inffixed.h`. It is the decompression backend used by zlib APIs and by gzip-file read code.

Risks: state transitions are security-sensitive because malformed compressed input is attacker-controlled in many applications. High-risk areas include bit-buffer rollback, table length validation, distance-too-far handling, checksum/trailer byte order, dictionary ID validation, and window wrap copying. `BUILDFIXED` uses static first-call initialization and is documented as not thread-safe.

Test signals: run zlib's inflate conformance vectors, gzip header/trailer cases, raw deflate, preset dictionaries, small input/output chunking, sync recovery after data errors, `inflateCopy`, `inflatePrime`, `inflateMark`, and strict invalid-distance cases. Fuzz compressed input under ASan/UBSan and compare output/errors against a known-good zlib.
