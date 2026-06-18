# File Research: sources/local-fs/e2fsprogs/e2fsck/problem.h

This header defines the public problem-code namespace and context structure used by e2fsck passes when reporting and repairing filesystem inconsistencies.

Core types:
- `problem_t` is a 32-bit problem code.
- `struct problem_context` carries optional fields used by message formatting and structured logs: error code, inode numbers, directory inode, inode pointer, dirent pointer, block numbers, logical block count, group, checksums, generic numeric fields, and string data.

Latch definitions:
- `PR_LATCH_MASK` extracts latch bits from problem flags.
- Latches group repeated repair decisions: illegal inode blocks, bad-block inode blocks, inode/block bitmaps, relocation hints, duplicate blocks, low dtime/orphan refugees, oversized inodes, directory optimization, group checksums, and extent optimization.
- `PRL_*` flags record yes/no, latched, and suppress state.

Problem-code layout:
- Pre-pass 1 codes start at `0x000001`.
- Pass 1 starts at `0x010000`.
- Pass 1B/1C/1D/1E occupy `0x011000` through `0x014000`.
- Pass 2 starts at `0x020000`.
- Pass 3 starts at `0x030000`, pass 3A at `0x031000`.
- Pass 4 starts at `0x040000`.
- Pass 5 starts at `0x050000`.
- Post-pass 5 starts at `0x060001`.

Notable groups:
- Pre-pass 1 covers superblock, journal, group descriptor, quota, MMP, metadata checksum, resize inode, orphan list, and orphan-file validation.
- Pass 1 covers inode/block/extent/EA/inline-data/casefold/encryption/quota/orphan-file validation.
- Pass 2 covers directory entries, filetypes, htree structure, checksums, encrypted/casefolded directory consistency, and EA-inode directory links.
- Pass 3 and 3A cover directory connectivity and rehash/optimization.
- Pass 4 covers link counts and EA inode refcounts.
- Pass 5 covers bitmap differences, padding, group summary counters, uninitialized group flags, and bitmap checksums.
- Post-pass 5 covers journal recreation, quota updates, block-group checksums, flush errors, and orphan-file cleanup.

Declared API:
- `fix_problem()`
- `end_problem_latch()`
- `set_latch_flags()`
- `get_latch_flags()`
- `clear_problem_context()`
- `print_e2fsck_message()`

Integration points:
- All pass files include this header to report problems by stable numeric code.
- `problem.c` supplies the table mapping these codes to text and behavior.
- Message formatting uses `problem_context` fields to expand symbolic placeholders.

Risk notes:
- Codes are externally meaningful to logs, tests, translation strings, and configuration profiles, so renumbering is risky.
- Comments serve as a compact semantic registry; adding a code requires synchronized updates in `problem.c`.
