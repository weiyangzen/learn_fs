# File Research: sources/os/linux/linux/fs/nls/nls_cp737.c

Implements Linux NLS support for DOS/OEM codepage 737, described as Greek. It follows the generated NLS table pattern with exact mappings only.

`charset2uni[256]` maps ASCII/control bytes directly for `0x00-0x7f`; the upper half maps primarily Greek uppercase/lowercase letters, Greek accented letters, and the common DOS line/box drawing range. Reverse Unicode lookup uses sparse pages `00`, `03`, `20`, `22`, and `25`, matching the file’s Greek, punctuation/math, and box-drawing coverage.

`uni2char()` is the standard generated lookup routine: it checks output capacity, splits `wchar_t` into page and offset, looks up `page_uni2charset`, returns one output byte for an exact mapping, and returns `-EINVAL` otherwise. `char2uni()` maps a byte through `charset2uni` and rejects mappings that resolve to `0x0000`.

The `nls_table` registers charset `"cp737"` and provides the local case conversion tables. The init/exit functions call `register_nls()` and `unregister_nls()`. Module metadata names `NLS Codepage 737 (Greek)` and uses `Dual BSD/GPL`.
