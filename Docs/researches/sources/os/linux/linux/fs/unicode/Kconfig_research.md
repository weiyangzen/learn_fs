# File Research: sources/os/linux/linux/fs/unicode/Kconfig

## Purpose
Defines kernel configuration options for filesystem UTF-8 normalization/casefolding support and its KUnit tests.

## Main Contents
- `UNICODE`: tristate option for UTF-8 NFD normalization and NFD+casefold support.
- Help text explains that when built as a module, the large casefolding table is requested only when a filesystem needs it.
- `UNICODE_NORMALIZATION_KUNIT_TEST`: tristate KUnit test option depending on `UNICODE && KUNIT`, defaulting to `KUNIT_ALL_TESTS`.

## Important Design Points
- Unicode support can be built-in, modular, or disabled.
- Tests are independently selectable but require both Unicode support and KUnit.

## Cross-File Relationships
- `Makefile` builds `unicode.o`, `utf8data.o`, and KUnit test objects based on these symbols.
- Filesystems using `linux/unicode.h` depend on `CONFIG_UNICODE`.

## Risks / Review Notes
- If `UNICODE=m`, runtime users depend on symbol/module availability for `utf8_data_table`.
