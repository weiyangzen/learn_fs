# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzlib.c

This file provides libbzip2 configuration and default allocation helpers.

Functions:
- `bz_config_ok`: verifies expected primitive sizes: `int` 4, `short` 2, `char` 1.
- `default_bzalloc`: allocates `items * size` with `malloc`.
- `default_bzfree`: frees non-null allocations.
- `bz_internal_error`: exits the process.

Notable implementation details:
- This is part of the split Plan 9-modified bzip2 library.
- `bz_internal_error` is marked as RSC-added replacement for missing original behavior.

Risks and caveats:
- `default_bzalloc` does not check multiplication overflow.
- Internal errors terminate with `exit(1)` and do not print context here.
