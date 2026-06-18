# File Research: sources/os/linux/linux/fs/nls/nls_cp775.c

Implements Linux NLS support for codepage 775, described as Baltic Rim. It is a generated single-byte charset translation module.

The byte-to-Unicode table preserves ASCII/control mappings in the low half and maps the high half to Baltic Latin characters, punctuation/currency symbols, and DOS box/block drawing characters. Reverse mapping is split across Unicode pages `00`, `01`, `20`, `22`, and `25`, which reflects Latin-1, Latin Extended-A, punctuation/math, and box drawing coverage.

The conversion callbacks are the generated NLS template. `uni2char()` enforces `boundlen > 0`, then uses `page_uni2charset[ch][cl]` where available; zero table entries mean unmappable and return `-EINVAL`. `char2uni()` returns exactly one wide character unless the selected byte maps to `0x0000`.

The module registers charset `"cp775"` through `struct nls_table`, with codepage-specific lower/upper byte case maps. Module registration is handled by `init_nls_cp775()` and `exit_nls_cp775()`. Metadata describes `NLS Codepage 775 (Baltic Rim)` and declares `Dual BSD/GPL`.
