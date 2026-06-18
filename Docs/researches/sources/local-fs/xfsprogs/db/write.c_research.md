# File Research: sources/local-fs/xfsprogs/db/write.c

Implements expert-mode `xfs_db` write support for structured fields, raw data blocks, and strings.

Key responsibilities:
- Registers `write` only in expert mode.
- Dispatches writes through the current type handler.
- Supports `-c` to write corrupt data with bad CRC and `-d` to write invalid data while recalculating CRC.
- Converts input values from quoted strings, octal escapes, hex blobs, UUID-like hyphenated hex, and numeric literals.
- Writes bitfields with `setbitval`.
- Provides raw block operations: left/right shift, left/right rotate, sequence, random, and fill.
- Writes null-terminated string data for symlink/string mode.

Important behavior:
- Refuses writes when libxfs was opened readonly.
- Temporarily swaps buffer verifier ops to bypass or recalculate CRCs for corrupt/invalid data modes.
- `write_struct` resolves field paths with `flist_scan`/`flist_parse`, computes bit length, writes, persists, and prints the changed field.
- Data mode subcommands accept abbreviated names based on significant-character counts.
- Random fill uses `lrand48`, seeded by `clock()` during initialization.

Dependencies:
- Depends on current IO buffer/type, field metadata, flist parsing, bit manipulation, verifier callbacks, and `write_cur`.

Notable risks:
- Intended for destructive expert use; invalid combinations can corrupt metadata.
- Several block mutators report too-large lengths but continue operating.
- `write_block` checks `cmd->len_arg < argc` when parsing `from`/`to`, which appears to gate those arguments on the wrong command metadata field.
