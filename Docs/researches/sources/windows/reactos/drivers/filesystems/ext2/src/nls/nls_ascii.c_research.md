# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_ascii.c

Linux-derived ASCII NLS table module. It defines exact byte-to-Unicode mappings for the 7-bit ASCII range, reverse Unicode-to-byte page table for Unicode page `0x00`, and case-folding tables for ASCII uppercase/lowercase conversion.

`uni2char` accepts Unicode code points whose high byte indexes a populated page table and whose low byte maps to a nonzero byte; otherwise it returns `-EINVAL`, or `-ENAMETOOLONG` when no output space is available. `char2uni` maps one input byte through `charset2uni` and rejects NUL/zero mappings as invalid.

The exported `nls_table` is named `"ascii"` with no alias. Its init routine registers the table with `register_nls`, and its exit routine unregisters it. The module uses Linux `module_init`, `module_exit`, and dual BSD/GPL license declarations, as adapted for this driver’s Linux-compatibility layer.
