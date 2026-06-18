# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_log.h

FTL logging macros wrapping `spdk_log`.

Behavior:
- Prefixes messages with `[FTL][<dev name>]`, using `N/A` for null device.
- Provides error, warning, notice, info, and debug macros.

Role:
- Standardizes subsystem logging across FTL code.
