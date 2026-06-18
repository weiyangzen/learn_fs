# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/utils.c

Purpose: Miscellaneous Venti server utility functions.

Key behavior:
- Name helpers compare/copy/validate fixed-size arena names.
- Decimal parsing helpers detect overflow for 32-bit and 64-bit unsigned values.
- Error/log helpers format messages, optionally log by severity, and set `%r`.
- Allocation wrappers zero or poison memory, tag allocations, and abort/sysfatal on failure.
- Provides time, process creation, `IEntry` formatting, Venti formatter registration, millisecond clock, and bit counting.

Dependencies:
- Uses Plan 9 formatting, allocation tagging, thread process creation, Venti formatters, and server error conventions.

Notable details:
- `vtproc` ignores `proccreate` failure and always returns 0.
