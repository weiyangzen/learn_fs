# File Research: sources/os/linux/linux/fs/nls/nls_cp860.c

Implements Linux NLS support for codepage 860, described as Portuguese. This is a generated DOS/OEM charset module.

`charset2uni[256]` maps the lower half to ASCII/control values and the upper half to Portuguese/Western European Latin characters, DOS line/box drawing, Greek/math symbols, and block characters. Reverse Unicode pages are `00`, `03`, `20`, `22`, `23`, and `25`.

The conversion callbacks match the generated NLS model. `uni2char()` is exact-only and fails with `-EINVAL` for characters not represented in CP860. `char2uni()` performs direct byte lookup and rejects bytes whose forward mapping is `0x0000`.

The module registers charset `"cp860"` with local lower/upper byte maps and standard NLS init/exit routines. Metadata identifies `NLS Codepage 860 (Portuguese)` and `Dual BSD/GPL`.
