# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp1250.c

Generated Linux NLS module for Windows codepage CP1250, covering Central European Latin characters. It defines a 256-entry `charset2uni` table, reverse Unicode-to-codepage tables for Unicode pages `00`, `01`, `02`, `20`, and `21`, plus CP1250-specific lowercase and uppercase byte maps.

The conversion functions follow the common single-byte NLS pattern used throughout this directory. `uni2char` indexes `page_uni2charset` by Unicode high byte and rejects unmapped entries or insufficient output space. `char2uni` maps one byte to Unicode and rejects zero mappings. Case tables preserve ASCII folding and add CP1250-specific folding for accented Central European letters.

The module registers an `nls_table` with charset `"cp1250"` and no alias. `init_nls_cp1250` calls `register_nls`, `exit_nls_cp1250` calls `unregister_nls`, and the file declares Linux-style module init/exit and dual BSD/GPL licensing.
