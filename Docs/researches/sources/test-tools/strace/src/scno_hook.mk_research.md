# sources/test-tools/strace/src/scno_hook.mk

Purpose: make hook that forces `scno.h` to exist before regenerating `Makefile` for normal build targets.

Important APIs/types/functions: `MAKECMDGOALS` filtering and `Makefile: scno.h` dependency.

Control flow: if goals do not contain `clean` and do not start with `dist`, the fragment adds `scno.h` as a prerequisite of `Makefile`; clean and dist operations avoid this dependency.

State and persistence behavior: no direct file writes; it only changes make dependency graph evaluation.

Dependencies and integration points: included by `scno.am` through `$(eval include ...)`, avoiding automake's direct parsing of the dependency.

Risks: goal filtering is broad and string-based; unusual custom goals containing `clean` or starting with `dist` will skip the hook.

Test signals: invoke ordinary builds, clean targets, and dist targets and confirm `scno.h` is generated only when appropriate.
