# File Research: sources/os/linux/linux-stable/fs/unicode/Kconfig

## Summary
Adds Kconfig options for kernel UTF-8 normalization/casefolding support and its KUnit tests.

## Main Contents
- `CONFIG_UNICODE`: tristate UTF-8 NFD normalization and NFD+CF casefolding support.
- `CONFIG_UNICODE_NORMALIZATION_KUNIT_TEST`: tristate KUnit test module depending on `UNICODE && KUNIT`, defaulting with `KUNIT_ALL_TESTS`.

## Important Behavior
`UNICODE` can be built-in or modular. When modular, the large UTF-8 data table can be a separate loadable module requested only by filesystems that need it.

## Dependencies
Uses Kconfig tristate and KUnit dependency mechanisms.

## Risks
Filesystems using Unicode normalization need `CONFIG_UNICODE`; tests require both Unicode support and KUnit.
