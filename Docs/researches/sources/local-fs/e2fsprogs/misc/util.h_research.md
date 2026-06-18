# File Research: sources/local-fs/e2fsprogs/misc/util.h

## Purpose
Declares shared tune2fs/mke2fs helper globals and function prototypes implemented in `util.c`.

## Key Elements
Exports journal configuration globals: `journal_size`, `journal_fc_size`, `journal_flags`, `journal_device`, and `journal_location_string`. Declares optional fallback `strcasecmp`, program-name extraction, confirmation prompt, journal option parsing, mount checking, journal sizing, check-policy printing, and MMP message dumping.

## Dependencies
The prototypes reference `struct ext2fs_journal_params`, `ext2_filsys`, and `struct mmp_struct`, so including files must already have suitable ext2fs declarations in scope or include this after ext2fs headers.

## Behavior/Risks
The header has no include guard. It exposes mutable global journal state, which keeps the command-line utility code simple but makes reentrant or repeated library-style use more fragile.
