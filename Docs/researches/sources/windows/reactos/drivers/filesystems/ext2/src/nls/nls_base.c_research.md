# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_base.c

Shared Linux NLS support layer embedded in the Ext2Fsd driver. It provides the global `struct nls_table *tables` registry, `nls_lock`, UTF-8 conversion helpers, NLS table registration and lookup, and exported symbols consumed by individual codepage modules and driver filename conversion code.

The UTF-8 section uses a table-driven decoder/encoder for one- through six-byte sequences. `utf8_mbtowc` validates continuation bytes and overlong ranges, `utf8_mbstowcs` converts a byte string to wide characters while skipping invalid bytes, `utf8_wctomb` emits the shortest matching UTF-8 sequence within `maxlen`, and `utf8_wcstombs` converts wide strings to UTF-8 while skipping unencodable characters.

`register_nls` and `unregister_nls` maintain the global linked list under `spin_lock`, reject null, duplicate, busy, or missing tables, and update each table’s `next` pointer. `find_nls` matches by charset or alias and uses `try_module_get`; `load_nls` first checks built-ins and can request a module when `CONFIG_KMOD` is enabled; `unload_nls` releases the module owner.

The second half defines a simple identity-like single-byte default mapping table, including byte-to-Unicode, reverse page `0x00`, and ASCII case folding. The default-table loader is disabled under `#if 0 // Masked by Matt`, but export declarations still include `load_nls_default`. This file is the central contract used by the codepage modules listed in this group.
