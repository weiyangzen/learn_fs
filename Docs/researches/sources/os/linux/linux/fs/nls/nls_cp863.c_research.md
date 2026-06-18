# File Research: sources/os/linux/linux/fs/nls/nls_cp863.c

Implements Linux NLS support for codepage 863, described as Canadian French. It follows the generated Linux NLS table structure.

The byte-to-Unicode table maps ASCII/control values directly and maps the high byte range to French/Western Latin letters, selected symbols, and DOS box/block drawing characters. Reverse Unicode pages are `00`, `01`, `03`, `20`, `22`, `23`, and `25`.

`uni2char()` enforces a positive output bound and uses sparse reverse tables for exact mappings. Missing reverse entries return `-EINVAL`. `char2uni()` maps one byte through `charset2uni` and rejects `0x0000`.

The module registers charset `"cp863"` with codepage-specific case conversion arrays. Standard module init/exit functions register and unregister the NLS table. Metadata identifies `NLS Codepage 863 (Canadian French)` and `Dual BSD/GPL`.
