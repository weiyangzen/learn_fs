# File Research: sources/os/linux/linux/fs/unicode/mkutf8data.c

## Purpose
Host-side generator that reads Unicode Character Database files and emits `utf8data.c`, a compact trie table used by the kernel UTF-8 normalization and casefolding runtime.

## Main Contents
- Command-line configurable inputs and output:
  - Age, combining class, core properties, UnicodeData, case folding, normalization corrections, normalization tests, and output C file.
- Unicode version handling:
  - Packs major/minor/revision into integer ages.
  - Builds `ages[]` and generation indexes used by trie leaves.
- UTF-8 helpers:
  - `utf8encode()`, `utf8decode()`, `utf32valid()`.
  - Valid Unicode range is limited to `0x0..0x10ffff`, with surrogates removed later.
- Compact trie builder:
  - `struct tree` and `struct node`.
  - `insert()` builds bitwise UTF-8 tries and collapses fully populated identical leaves.
  - `prune()` removes redundant singleton paths.
  - `mark_nodes()`, `index_nodes()`, `size_nodes()`, and `emit()` compute and serialize compact trie nodes/leaves.
- Unicode data model:
  - `struct unicode_data` stores code point, combining class, generation, correction age, UTF-32 and UTF-8 decompositions.
  - Global `unicode_data[0x110000]` covers all Unicode scalar slots.
  - `corrections` stores normalization corrections by version.
- Parsers:
  - `age_init()` reads `DerivedAge.txt` and marks defined code point generations.
  - `ccc_init()` reads canonical combining classes.
  - `nfdi_init()` reads canonical decompositions from `UnicodeData.txt`, ignoring compatibility decompositions.
  - `nfdicf_init()` reads common/full case folding from `CaseFolding.txt`.
  - `ignore_init()` maps `Default_Ignorable_Code_Point` entries to empty decompositions.
  - `corrections_init()` reads normalization corrections.
- Decomposition expansion:
  - `hangul_decompose()` prepares Hangul decompositions but marks them with a cookie so runtime handles them algorithmically.
  - `nfdi_decompose()` recursively expands canonical decompositions and seeds NFDICF when no casefold exists.
  - `nfdicf_decompose()` recursively expands casefolding decompositions.
  - `utf8_init()` converts UTF-32 decomposition arrays to UTF-8 strings.
- Generator self-check runtime:
  - Contains local trie lookup, age, length, cursor, and `utf8byte()` implementations mirroring kernel runtime behavior.
  - `trees_verify()` checks trie contents against source data.
  - `normalization_test()` validates generated NFDI behavior against `NormalizationTest.txt`.
- `write_file()` emits:
  - `utf8agetab`
  - `utf8nfdicfdata`
  - `utf8nfdidata`
  - packed `utf8data[]`
  - exported `utf8_data_table`
- `main()` orchestrates parse, decompose, build, verify, test, and output.

## Important Design Points
- Two normalization forms are generated:
  - `nfdi`: NFD plus removal of default ignorables.
  - `nfdicf`: NFD plus removal of default ignorables plus full casefolding.
- Leaves encode generation, canonical combining class, and optional decomposition string.
- Combining class reordering is not pre-expanded into every string; runtime cursors sort by CCC while scanning.
- Hangul syllable decompositions are represented with a marker and synthesized algorithmically at runtime to save table space.
- Trees are generated for correction/version boundaries so older Unicode versions can be supported from one data blob.
- The emitted trie format must match the constants and traversal code duplicated in `utf8-norm.c`.

## Cross-File Relationships
- Built as a host tool by `fs/unicode/Makefile`.
- Emits C code included in kernel builds as `utf8data.c`.
- Generated output defines `utf8_data_table`, consumed by `utf8-core.c` and interpreted by `utf8-norm.c`.
- Shares structure and trie format assumptions with `utf8n.h`.

## Risks / Review Notes
- Parsers use fixed-size line buffers and fixed-size decomposition arrays based on Unicode assumptions; new UCD formats or longer mappings can break generation.
- Memory allocation failures are generally not checked; this is a host build tool but still a robustness limitation.
- Runtime trie lookup code is duplicated between generator and kernel runtime; format changes must update both.
- Normalization correctness depends on UCD file consistency and successful `normalization_test()`.
