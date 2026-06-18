# File Research: sources/os/linux/linux-stable/fs/nls/nls_koi8-ru.c

Purpose: Linux NLS wrapper for KOI8-RU, described as Belarusian, implemented as a small delta on top of `koi8-u`.

Core structures and data:
- `static struct nls_table *p_nls` stores the loaded `koi8-u` backend.
- The public `nls_table` defines charset `"koi8-ru"` and custom `uni2char`/`char2uni` callbacks.
- Case tables are copied from the underlying `koi8-u` table at init time.

Important behavior:
- `uni2char()` checks the few Unicode values where KOI8-RU differs from KOI8-U. U+040E maps to byte `0xbe`, U+045E maps to `0xae`, and U+255D/U+256C return 0 in the special branch; other cases delegate to `koi8-u`.
- `char2uni()` has a suspicious-looking branch: when `(*rawstring & 0xef) != 0xae`, it returns U+040E or U+045E based on bit `0x10`; otherwise it delegates to `koi8-u`.
- `init_nls_koi8_ru()` loads `koi8-u`, inherits its case tables, and registers the wrapper.
- `exit_nls_koi8_ru()` unregisters and unloads the base charset.

Dependencies and interfaces:
- Requires the `koi8-u` NLS module to be loadable.
- Exposes normal `nls_table` callbacks to NLS core.

Design notes and risks:
- The file is intentionally tiny and relies on `koi8-u` for almost all behavior.
- The `char2uni()` condition differs from the comment's “two characters” wording; the current expression sends most bytes into the special mapping branch and only delegates for bytes matching the masked pattern. This should be treated carefully if audited or modified.
- Returning `0` from `uni2char()` for U+255D/U+256C is not the usual negative errno pattern used by generated modules.
