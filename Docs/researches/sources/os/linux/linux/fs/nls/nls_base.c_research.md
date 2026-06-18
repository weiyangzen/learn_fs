# File Research: sources/os/linux/linux/fs/nls/nls_base.c

Implements the shared Linux native language support registry and UTF conversion helpers.

Key behavior:
- Maintains a global linked list of `struct nls_table` entries protected by `nls_lock`.
- `__register_nls()` adds a table and rejects duplicate/already-linked registrations.
- `unregister_nls()` removes a registered table.
- `find_nls()` searches by charset or alias and pins the owning module with `try_module_get()`.
- `load_nls()` requests `nls_<charset>` modules on demand.
- `unload_nls()` drops the module reference.
- `load_nls_default()` tries `CONFIG_NLS_DEFAULT`, falling back to the built-in `default_table`.
- Implements UTF helpers:
  - `utf8_to_utf32()`
  - `utf32_to_utf8()`
  - `utf8s_to_utf16s()`
  - `utf16s_to_utf8s()`
- UTF validation rejects overlong encodings, surrogate code points, and code points above `0x10ffff`.

Important interactions:
- Exports NLS registry and UTF conversion symbols for filesystem code and charset modules.
- The built-in `default_table` is a single-byte identity-style table for bytes `0x01` through `0xff`, with ASCII-style case maps.
