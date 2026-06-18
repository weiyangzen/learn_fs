# File Research: sources/os/linux/linux-stable/fs/ntfs/unistr.c

This file implements legacy NTFS Unicode string comparison, collation, duplication, and conversion between mounted NLS encoding and NTFS little-endian UTF-16 strings.

Main responsibilities:
- Compares NTFS UTF-16 names case-sensitively or case-insensitively using the volume `$UpCase` table.
- Collates filename attributes for index ordering and rejects invalid Windows filename characters during collation.
- Converts user/NLS strings into little-endian UTF-16 for NTFS names and labels.
- Converts UTF-16 names back to NLS/UTF-8 for presentation.
- Duplicates bounded UTF-16 strings safely.

Important functions and data:
- `legal_ansi_char_array[]` marks low ASCII characters invalid or special for collation.
- `ntfs_are_names_equal()` and `ntfs_names_are_equal()` are equality helpers; the latter treats zero-length equal names explicitly.
- `ntfs_collate_names()` compares two names and can return a caller-specified error value if `name1` contains invalid `"`, `*`, `<`, `>`, or `?` characters.
- `ntfs_ucsncmp()` and `ntfs_ucsncasecmp()` are endian-aware UTF-16 comparison primitives.
- `ntfs_file_compare_values()` compares `FILE_NAME` attribute values using NTFS collation.
- `ntfs_nlstoucs()` allocates and fills an NTFS UTF-16 output string, using UTF-8 conversion when `vol->nls_utf8` is set or the mounted NLS table otherwise.
- `ntfs_ucstonls()` converts UTF-16 to UTF-8/NLS, allocating or growing the output buffer when allowed.
- `ntfs_ucsndup()` duplicates up to `maxlen` UTF-16 characters and always terminates.

Notable implementation details:
- All routines assume strings are stored as little-endian Unicode.
- `ntfs_nlstoucs()` uses `ntfs_name_cache` for normal NTFS maximum-length names and `kvmalloc()` for larger caller-provided limits such as volume labels.
- Conversion failures distinguish invalid character sequences from too-long names where possible.

Research notes:
- This file is used by directory lookup, index collation, volume label handling, and any code converting Linux-visible names to NTFS on-disk names.
- Correct use depends on the volume `upcase` table initialized in `super.c`.
