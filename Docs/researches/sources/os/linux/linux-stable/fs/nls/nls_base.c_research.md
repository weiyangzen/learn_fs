# File Research: sources/os/linux/linux-stable/fs/nls/nls_base.c

This file is the core Linux filesystem Native Language Support implementation. It provides UTF conversion helpers, NLS table registration/loading, and the built-in fallback default table.

The UTF-8/UTF-32 path uses `utf8_table[]` to validate sequence length, bit masks, minimum encoded value, `UNICODE_MAX`, and surrogate exclusion. `utf8_to_utf32()` returns the number of consumed bytes or `-EILSEQ`/`-EOVERFLOW`. `utf32_to_utf8()` emits UTF-8 for a scalar value, rejects invalid Unicode and surrogate code points, and returns `-EOVERFLOW` when the output buffer is too small.

The UTF-8/UTF-16 helpers support native, little-endian, and big-endian UTF-16 through `put_utf16()` and `get_utf16()`. `utf8s_to_utf16s()` converts UTF-8 input to UTF-16 code units and emits surrogate pairs for non-BMP values. `utf16s_to_utf8s()` converts UTF-16 strings to UTF-8, skips malformed surrogate input, and stops when a valid character no longer fits in the output buffer.

The NLS registry is a global linked list rooted at `tables`, protected by `nls_lock`. `__register_nls()` inserts a table after checking for double registration, `unregister_nls()` removes a table, `find_nls()` matches by charset or alias while taking a module reference, `load_nls()` invokes module autoloading with `nls_%s`, and `unload_nls()` drops the module reference. `load_nls_default()` attempts `CONFIG_NLS_DEFAULT` and falls back to `default_table`.

The built-in `default_table` is an identity-style 8-bit mapping for Unicode page 0, with ASCII case folding for the alphabetic ASCII range. It uses the same `uni2char()` and `char2uni()` skeleton as generated modules, but spans all `0x00`-`0xff` byte values in `charset2uni` and `page00`.

Exports include UTF conversion functions and NLS registry APIs. Module metadata identifies this as `Base file system native language support` under `Dual BSD/GPL`.
