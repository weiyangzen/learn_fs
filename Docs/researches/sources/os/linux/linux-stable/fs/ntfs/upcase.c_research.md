# File Research: sources/os/linux/linux-stable/fs/ntfs/upcase.c

This file generates the legacy NTFS default Unicode uppercase mapping table in little-endian form.

Main responsibilities:
- Allocates a `default_upcase_len` entry `__le16` table.
- Initializes each character to identity mapping.
- Applies compact range and word override tables to produce NTFS uppercase mappings.

Important data:
- `uc_run_table` stores contiguous ranges with a constant additive delta.
- `uc_dup_table` stores alternating pairs where the odd/lowercase entry maps to the previous entry.
- `uc_word_table` stores individual codepoint overrides.

Important function:
- `generate_default_upcase()` returns a freshly allocated table or `NULL` on allocation failure.

Research notes:
- The generated table is shared by volumes in `super.c` when their on-disk `$UpCase` matches the default.
- The table is little-endian because NTFS strings and upcase entries are little-endian on disk.
