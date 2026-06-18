# File Research: sources/os/linux/linux/fs/nls/nls_cp861.c

Implements Linux NLS support for codepage 861, described as Icelandic. It is generated from Unicode charset data and only supports exact reverse mappings.

The forward table maps low bytes to ASCII/control values and high bytes to Icelandic/Western Latin letters, DOS drawing characters, and symbols. Reverse Unicode pages are `00`, `01`, `03`, `20`, `22`, `23`, and `25`, reflecting Latin, Greek/math, symbol, and box-drawing coverage.

`uni2char()` checks `boundlen`, indexes the sparse reverse page table, and returns `-EINVAL` for unmappable Unicode. `char2uni()` returns one `wchar_t` from `charset2uni` unless that mapping is `0x0000`.

The registered charset is `"cp861"` with CP861 lower/upper case tables. Lifecycle is handled through `register_nls()` and `unregister_nls()`. Module metadata is `NLS Codepage 861 (Icelandic)` with `Dual BSD/GPL`.
