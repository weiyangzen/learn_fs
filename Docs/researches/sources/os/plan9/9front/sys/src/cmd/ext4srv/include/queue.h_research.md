# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/queue.h

## Purpose
Provides BSD-style intrusive collection macros for 9front's `ext4srv` support code.

## Key Elements
Defines `SLIST`, `STAILQ`, `LIST`, and `TAILQ` head/entry declarations plus initialization, insertion, removal, traversal, safe traversal, concatenation, swap, and predecessor/last access helpers. The implementation uses Plan 9 `nil` and `__containerof`-style pointer recovery for some reverse/last operations.

## Dependencies
No runtime dependencies; this is a macro-only header adapted from BSD queue macros. Debug/check/tracing hooks such as `QMD_TRACE_*`, `QMD_*_CHECK_*`, and `TRASHIT` are compiled as no-ops here.

## Behavior/Risks
Intrusive macros mutate caller-owned link fields and assume elements are already linked in the expected list. Singly linked arbitrary removals are linear. Since validation hooks are disabled, corrupted link state will usually fail later as pointer misuse rather than at the macro boundary.
