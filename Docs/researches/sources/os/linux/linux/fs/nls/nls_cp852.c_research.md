# File Research: sources/os/linux/linux/fs/nls/nls_cp852.c

Implements Linux NLS support for codepage 852, described as Central/Eastern Europe. It is generated from Unicode charset tables with exact reverse mappings only.

The forward table maps ASCII/control bytes in the lower half and Central/Eastern European Latin characters in the upper half, including Latin Extended-A/B code points, plus box/block drawing characters. Reverse lookup pages are `00`, `01`, `02`, and `25`, matching Latin-1, Latin Extended-A, Latin Extended-B, and box drawing.

`uni2char()` follows the common sparse-page reverse lookup and reports `-EINVAL` when a Unicode character lacks an exact CP852 byte. `char2uni()` maps one byte through the forward table and treats `0x0000` as invalid.

The `nls_table` registers charset `"cp852"` with CP852-specific case maps. Init and exit are standard `register_nls()`/`unregister_nls()` wrappers. Module metadata says `NLS Codepage 852 (Central/Eastern Europe)` and `Dual BSD/GPL`.
