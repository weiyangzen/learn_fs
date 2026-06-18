# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp737.c

Generated Linux NLS module for DOS codepage CP737, a Greek codepage. Its byte-to-Unicode table maps ASCII/control bytes, Greek uppercase and lowercase letters, accented Greek letters, box-drawing/block glyphs, and selected math symbols. Reverse Unicode maps are present for pages `00`, `03`, `20`, `22`, and `25`.

`uni2char` and `char2uni` are the standard exact single-byte routines used by the surrounding NLS files. The case-folding tables include ASCII folding plus Greek byte-pair folding for the codepage’s uppercase/lowercase Greek range, while leaving drawing and symbol bytes stable.

The module registers charset `"cp737"` with no alias. `init_nls_cp737` and `exit_nls_cp737` connect it to the shared NLS registry, with Linux-style module declarations and dual BSD/GPL license metadata.
