# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/common.c

This file provides common utility functions for the VFAT checker.

Core responsibilities:
- ReactOS `exit` terminates the current process through `NtTerminateProcess`.
- `die_func` and `pdie_func` print unrecoverable errors through ReactOS debug/print helpers and terminate.
- ReactOS allocation helpers `vfalloc`, `vfcalloc`, and `vffree` wrap process heap allocation.
- `qalloc` and `qfree` manage a linked list of allocations for batch cleanup.
- `min` returns the smaller integer.
- `get_key` implements interactive prompting in non-ReactOS builds; ReactOS returns `0`.

Risk points:
- `die`/`pdie` are process-terminating, which is harsh for a library entry point.
- ReactOS `vfcalloc` returns NULL without terminating, unlike `vfalloc`.
- `get_key` returning `0` means any unexpectedly interactive path may take default/fallback behavior rather than receiving real input.
