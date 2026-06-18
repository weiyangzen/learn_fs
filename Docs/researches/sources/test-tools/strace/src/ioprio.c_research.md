# sources/test-tools/strace/src/ioprio.c

Purpose: decodes Linux I/O priority syscalls and provides a reusable `print_ioprio` formatter for priority values.

Important APIs/types/functions: `sprint_ioprio`, `print_ioprio`, `ioprio_print_who`, `SYS_FUNC(ioprio_get)`, `SYS_FUNC(ioprio_set)`, `IOPRIO_CLASS_SHIFT`, `IOPRIO_PRIO_CLASS`, `IOPRIO_PRIO_DATA`, and xlat tables `ioprio_who`/`ioprio_class`.

Control flow: `sprint_ioprio` splits a priority word into class and data, formats `IOPRIO_PRIO_VALUE(...)`, and respects xlat lookup fallback. `ioprio_get` prints `which` and PID-like `who` on entry, then on successful exit attaches a decoded return string unless raw xlat mode is active. `ioprio_set` prints `which`, dispatches `who` through process or process-group PID printers, and formats the `ioprio` argument according to xlat verbosity.

State and persistence behavior: no persistent state beyond `tcp->auxstr` for `ioprio_get` return annotation. `sprint_ioprio` uses a static buffer, so callers must consume the string immediately.

Dependencies and integration points: depends on `defs.h`, `xstring.h`, PID namespace-aware `printpid`, xlat verbosity, and the generated priority xlat tables. `print_ioprio` can be reused by other decoders that expose kernel I/O-priority words.

Risks: static formatter storage is not reentrant; xlat verbosity changes output shape substantially; unknown `which` values are intentionally printed numerically and should not be treated as PIDs.

Test signals: cover raw/abbrev/verbose xlat modes, `IOPRIO_WHO_PROCESS`, `IOPRIO_WHO_PGRP`, unknown `which`, successful `ioprio_get` return decoding, and syscall-error exit behavior.
