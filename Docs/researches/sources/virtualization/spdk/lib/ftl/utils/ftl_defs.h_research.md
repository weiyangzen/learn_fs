# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_defs.h

Common FTL utility definitions.

Contents:
- KiB/MiB/GiB/TiB constants if not already defined.
- `ftl_abort()` assert-plus-abort helper.
- `ftl_bug(cond)` hard abort on unexpected condition.
- Generic invalid values for band IDs and physical IDs.

Role:
- Provides fail-fast invariants used throughout FTL metadata and upgrade code.
