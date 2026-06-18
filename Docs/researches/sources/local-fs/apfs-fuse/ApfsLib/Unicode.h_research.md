# File Research: sources/local-fs/apfs-fuse/ApfsLib/Unicode.h

This header declares the Unicode normalization helpers used by APFS filename logic. It exposes per-code-point normalization/folding, canonical reordering, and whole-string normalization/folding.

The public functions are `normalizeOptFoldU32Char()`, `CanonicalReorder()`, and `NormalizeFoldString()`. The whole-string API uses `std::vector<char32_t>` for input/output and a boolean to enable case folding.

This header has no implementation state. The generated lookup data is hidden in `UnicodeTables_v10.h` and included only by `Unicode.cpp`.
