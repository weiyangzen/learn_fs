# File Research: sources/local-fs/apfs-fuse/ApfsLib/Util.cpp

This file implements shared APFS utility functions: checksums, block validation, zero checks, hex/debug formatting, UUID/key formatting, UTF-8/UTF-32 helpers, APFS filename hashing/comparison, password input, multiple compression decoders, an integer log2 helper, and debug logging.

Checksum logic includes `Fletcher64()`, used by `VerifyBlock()` to validate APFS object checksums. `VerifyBlock()` rejects all-zero and all-ones checksums, computes Fletcher64 over the block data after the checksum field and then over the checksum field, and expects the final result to be zero. `IsZero()` and `IsEmptyBlock()` provide byte-wise and 64-bit-word zero checks.

Formatting helpers include `DumpHex()`, `DumpBuffer()`, `uuidstr()`, `hexstr()`, `dump_utf8()`, and `dump_utf32()`. These are used by debug paths, dump utilities, crypto diagnostics, and block inspection code.

Filename helpers include `HashFilename()`, `apfs_strncmp()`, and `StrCmpUtf8NormalizedFolded()`. `HashFilename()` converts UTF-8 to UTF-32, normalizes and optionally folds with the APFS Unicode code, computes CRC32C using polynomial `0x1EDC6F41`, and packs the low 22 hash bits with the APFS directory-record name length. `StrCmpUtf8NormalizedFolded()` normalizes both strings and performs lexicographic UTF-32 comparison. `apfs_strncmp()` is a bounded byte comparison for APFS byte strings.

`Utf8toUtf32()` implements a small UTF-8 decoder. It accepts up to four-byte sequences, stops at NUL, and returns false on malformed continuation bytes or invalid leading bytes. It does not enforce all modern UTF-8 validity constraints such as overlong encodings or Unicode scalar range exclusions.

`GetPassword()` reads a password line from stdin. On Linux/macOS it disables terminal echo with `termios`, restores terminal state, and prints a newline. Other platforms read normally.

Compression helpers support APFS compressed file/resource data: zlib (`DecompressZLib()`), Apple Data Compression-style backreferences (`DecompressADC()`), LZVN via lzfse’s decoder state, bzip2, LZFSE, and a custom `DecompressLZBITMAP()` decoder. `DecompressLZBITMAP()` parses a `ZBM` stream with flag `0x09`, handles stored blocks, token maps, RLE-expanded token streams, literal/distance/bitmap sections, and reconstructs output with backreferences.

Logging is controlled by global debug flags from `Global.h`. `log_debug()` prints only when `Dbg_Cmpfs` is enabled, `log_warn()` when `Dbg_Info` is enabled, and `log_error()` when `Dbg_Errors` is enabled. All log to global `g_log`, initialized to stderr.

Notable risks: several decompressors rely on assertions or minimal boundary checks and should not be treated as hardened parsers for hostile input. `DecompressADC()` asserts exact source/output consumption and may read/write past bounds before an assertion in malformed streams. `DecompressLZBITMAP()` has more explicit error checks but still contains assumptions such as flag `0x09` and fixed scratch sizing.
