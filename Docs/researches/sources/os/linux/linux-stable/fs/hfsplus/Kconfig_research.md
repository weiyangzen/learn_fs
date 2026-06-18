# File Research: sources/os/linux/linux-stable/fs/hfsplus/Kconfig

## Scope

Defines kernel configuration entries for HFS+ filesystem support and HFS+ KUnit tests.

## Configuration

- `HFSPLUS_FS` is a tristate block-device filesystem option. It depends on `BLOCK` and selects `BUFFER_HEAD`, `NLS`, `NLS_UTF8`, and `LEGACY_DIRECT_IO`.
- `HFSPLUS_KUNIT_TEST` builds HFS+ KUnit tests when `HFSPLUS_FS` and `KUNIT` are enabled, defaulting under `KUNIT_ALL_TESTS`.

## Risks And Invariants

The selected dependencies reflect implementation choices in this directory: buffer-head based block mapping, NLS/UTF-8 name conversion, and legacy direct I/O hooks. KUnit tests are explicitly development-only.
