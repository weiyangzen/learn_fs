# File Research: sources/os/linux/linux/fs/unicode/Makefile

## Purpose
Builds the kernel Unicode normalization objects and optionally regenerates the generated UTF-8 data table from Unicode Character Database text files.

## Main Contents
- Builds `unicode.o` from `utf8-norm.o` and `utf8-core.o` when `CONFIG_UNICODE` is set.
- Builds `utf8data.o` when `CONFIG_UNICODE` is enabled.
- Builds `tests/utf8_kunit.o` when `CONFIG_UNICODE_NORMALIZATION_KUNIT_TEST` is enabled.
- Declares `mkutf8data` as a host program.
- Default path copies `utf8data.c_shipped` into generated `utf8data.c`.
- `REGENERATE_UTF8DATA=1` path runs `mkutf8data` with UCD inputs:
  - `DerivedAge.txt`
  - `DerivedCombiningClass.txt`
  - `DerivedCoreProperties.txt`
  - `UnicodeData.txt`
  - `CaseFolding.txt`
  - `NormalizationCorrections.txt`
  - `NormalizationTest.txt`

## Important Design Points
- Normal kernel builds use checked-in generated data instead of requiring UCD files.
- Regeneration is explicit and depends on placing UCD text files in the source directory.
- `targets += utf8data.c` marks the generated data file as a kbuild target.

## Cross-File Relationships
- Host generator is implemented by `mkutf8data.c`.
- Generated `utf8data.c` includes `utf8n.h` and exports `utf8_data_table`.
- Runtime code in `utf8-core.c` loads the generated table via symbol lookup.

## Risks / Review Notes
- Regeneration depends on exact UCD file names and parser expectations in `mkutf8data.c`.
- Generated output must stay compatible with trie reader logic in `utf8-norm.c`.
