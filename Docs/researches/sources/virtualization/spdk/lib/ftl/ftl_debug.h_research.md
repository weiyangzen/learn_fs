# File Research: sources/virtualization/spdk/lib/ftl/ftl_debug.h

## Purpose
Declares and conditionally stubs FTL debug helpers.

## Contents
- In `DEBUG`, declares `ftl_band_validate_md()` and `ftl_dev_dump_bands()`.
- In non-debug builds, implements `ftl_band_validate_md()` as an asynchronous success callback on the core thread and `ftl_dev_dump_bands()` as no-op.
- `ftl_debug_inject_trim_error()` aborts after 256 trims when `FTL_CRASH_ON_TRIM` is set in debug builds; otherwise no-op.
- Always declares `ftl_dev_dump_stats()`.

## Dependencies
Includes FTL internal, band, and core headers.
