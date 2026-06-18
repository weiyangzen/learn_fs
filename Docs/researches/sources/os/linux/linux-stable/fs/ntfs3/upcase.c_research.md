# File Research: sources/os/linux/linux-stable/fs/ntfs3/upcase.c

Purpose: Provides NTFS Unicode case-folded comparison and hashing helpers using the mounted volume's `$UpCase` table.

Key responsibilities:
- `upcase_unicode_char()` uppercases ASCII `a`-`z` directly and otherwise indexes the `$UpCase` table.
- `ntfs_cmp_names()` compares two little-endian UTF-16 names, supporting case-sensitive, case-insensitive, and `bothcase` tie-breaking behavior.
- `ntfs_cmp_names_cpu()` compares a CPU-endian `struct cpu_str` to a little-endian `struct le_str`.
- `ntfs_names_hash()` feeds upcased UTF-16 code units into Linux `partial_name_hash()`.

Important invariants:
- When `bothcase` and an upcase table are supplied, exact-case differences are remembered as `diff1`, but case-insensitive comparison decides primary ordering; exact-case difference breaks ties.
- With no upcase table, comparisons are raw code-unit comparisons.
- Length difference is returned when common prefixes match.

Dependencies:
- Uses `$UpCase` loaded and possibly shared by `super.c`.
- Used by record/attribute collation, directory lookup, and case-insensitive dentry operations.

Risk notes:
- The helpers operate on UTF-16 code units, not full Unicode scalar/canonical equivalence.
- `upcase_unicode_char()` assumes the upcase table covers all 16-bit input values.
