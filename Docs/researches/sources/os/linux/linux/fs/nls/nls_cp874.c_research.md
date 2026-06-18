# File Research: sources/os/linux/linux/fs/nls/nls_cp874.c

Implements Linux NLS support for Thai codepage 874 and aliases it as TIS-620. This is the only file in the group that sets `.alias = "tis-620"` and emits `MODULE_ALIAS_NLS(tis-620)`.

The forward table maps ASCII/control bytes directly, marks several Windows-style undefined/control-extension positions as `0x0000`, maps selected punctuation in the `0x80-0x9f` area, and maps `0xa1-0xfb` primarily to Thai Unicode U+0E01 through U+0E5B. Reverse Unicode pages are `00`, `0e`, and `20`, corresponding to Latin-1/ASCII, Thai, and punctuation.

`uni2char()` follows the generated exact reverse lookup and returns `-EINVAL` for Unicode not present in CP874/TIS-620. `char2uni()` maps one byte through `charset2uni` and rejects undefined byte positions via the `0x0000` check.

The `nls_table` registers charset `"cp874"` with alias `"tis-620"` plus local lower/upper byte maps. Init/exit use `register_nls()` and `unregister_nls()`. Metadata is `NLS Thai charset (CP874, TIS-620)`, `Dual BSD/GPL`, and the TIS-620 NLS alias.
