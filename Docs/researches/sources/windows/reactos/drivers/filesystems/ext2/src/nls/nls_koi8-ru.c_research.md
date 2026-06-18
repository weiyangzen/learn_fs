# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_koi8-ru.c

This is a small wrapper module for `koi8-ru`, implemented by loading the `koi8-u` NLS table at init time and overriding the few mappings where KOI8-RU differs.

`init_nls_koi8_ru` calls `load_nls("koi8-u")`, copies the base table's case-conversion pointers, and registers a new table named `koi8-ru`. Exit unregisters the wrapper and unloads the base table.

`uni2char` special-cases U+040E/U+045E and selected box-drawing differences, otherwise delegates to `p_nls->uni2char`.

Research note: the `char2uni` branch condition appears inconsistent with the comment. It maps bytes when `((*rawstring & 0xef) != 0xae)`, which means most input bytes bypass the base table and become U+040E/U+045E. Given the comment that KOI8-RU and KOI8-U differ only on two characters, this looks like a likely inverted condition and a high-risk bug.

Dependency risk: if `koi8-u` is unavailable, registration fails with `-EINVAL`.
