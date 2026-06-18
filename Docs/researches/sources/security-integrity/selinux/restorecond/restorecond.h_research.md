# sources/security-integrity/selinux/restorecond/restorecond.h
# sources/security-integrity/selinux/restorecond/restorecond.h

Purpose: shared restorecond declarations for cross-module globals and functions.

Important APIs and types: declares global flags (`debug_mode`, `homedir`, `terminate`, `master_wd`, `run_as_user`, `r_opts`) and functions for user server startup, error exit, config reading, watch loop/list operations, and watch-list emptiness checks.

State and persistence: exposes mutable process globals used by root and user daemon paths.

Dependencies and integration points: included by `restorecond.c`, `watch.c`, `user.c`, `utmpwatcher.c`, and `stringslist.c`.

Risks and test signals: broad global sharing makes behavior sensitive to initialization order and cleanup. No direct tests target header contracts.
