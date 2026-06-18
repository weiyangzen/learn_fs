# File Research: sources/os/linux/linux/fs/nls/nls_koi8-ru.c

Purpose: Linux NLS wrapper for KOI8-RU, described as Belarusian, implemented as a small delta on top of `koi8-u`.

Core structures and data:
- `static struct nls_table *p_nls` stores the loaded `koi8-u` backend.
- Public `nls_table` registers charset `"koi8-ru"` with custom `uni2char` and `char2uni`.
- Case tables are copied from the loaded `koi8-u` table at init.

Important behavior:
- `uni2char()` handles the few KOI8-RU differences: U+040E maps to `0xbe`, U+045E maps to `0xae`, and U+255D/U+256C return `0` in the special branch; other values delegate to `koi8-u`.
- `char2uni()` has a notable condition: when `(*rawstring & 0xef) != 0xae`, it returns U+040E or U+045E based on bit `0x10`; otherwise it delegates to `koi8-u`.
- `init_nls_koi8_ru()` loads `koi8-u`, inherits case tables, and registers this wrapper.
- `exit_nls_koi8_ru()` unregisters and unloads the base charset.

Dependencies and interfaces:
- Requires the `koi8-u` NLS module to be loadable.
- Exposes standard `struct nls_table` callbacks.

Design notes and risks:
- This file relies on `koi8-u` for almost all behavior.
- The `char2uni()` condition is suspicious relative to the “differ only on two characters” comment; changes need careful testing.
- Returning `0` from `uni2char()` is unusual compared with the generated modules’ negative errno behavior.
