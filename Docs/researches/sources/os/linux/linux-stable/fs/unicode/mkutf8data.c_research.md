# File Research: sources/os/linux/linux-stable/fs/unicode/mkutf8data.c

## Summary
Host-side generator that parses Unicode Character Database files, builds compact versioned UTF-8 normalization tries for NFDI and NFDICF, verifies them, runs normalization tests, and emits `utf8data.c`.

## Key Components
- UCD input parsing: `age_init()`, `ccc_init()`, `nfdi_init()`, `nfdicf_init()`, `ignore_init()`, `corrections_init()`.
- Decomposition processing: `hangul_decompose()`, `nfdi_decompose()`, `nfdicf_decompose()`, `utf8_init()`.
- Trie operations: `insert()`, `prune()`, `mark_nodes()`, `index_nodes()`, `size_nodes()`, `emit()`, `trees_populate()`, `trees_reduce()`.
- Verification/testing: `verify()`, `trees_verify()`, `normalization_test()`.
- Runtime-equivalent lookup/cursor helpers used for generator self-tests.
- Output: `write_file()`.
- Entry point: `main()`.

## Important Behavior
The generator supports two normalization forms tailored for filenames: `nfdi` applies canonical NFD and removes default ignorables; `nfdicf` also applies full casefolding using C+F mappings.

Unicode ages are packed with `UNICODE_AGE()` and compressed into generation numbers. Generated leaves store generation, canonical combining class, and optional decomposition strings. This allows runtime filtering by supported Unicode version.

The code builds a compact binary trie over valid UTF-8 byte sequences. Internal nodes encode bit tests, next-byte transitions, relative offsets, and node/leaf flags. Subtrees with identical leaves are collapsed, then pruned further when singleton chains make identical decisions.

Multiple trees are generated for normalization correction ages and for the latest NFDI/NFDICF tables. Older correction trees share or forward to later trees where possible.

The parser reads canonical decomposition mappings from `UnicodeData.txt`, ignores compatibility forms, applies full casefold mappings from `CaseFolding.txt`, removes `Default_Ignorable_Code_Point` entries from `DerivedCoreProperties.txt`, and applies normalization corrections from `NormalizationCorrections.txt`.

Hangul syllables are decomposed algorithmically. The generator marks Hangul leaves with a special `HANGUL` cookie instead of storing every decomposition string.

Generated trie data is aligned and emitted as a static byte array plus `utf8agetab`, `utf8nfdicfdata`, `utf8nfdidata`, and exported `utf8_data_table`.

## Dependencies
Runs as a host C program using libc file I/O, `getopt`, allocation, assertions, and string parsing. Its output is consumed by `utf8-core.c` and `utf8-norm.c`.

## Risks
The parser depends on UCD text file formats and fixed maximum decomposition mapping length assumptions. Trie correctness depends on offset sizing stabilizing through repeated indexing/sizing passes. The generated data must match the runtime trie decoder in `utf8-norm.c`; the file intentionally contains a runtime-equivalent decoder for verification.
