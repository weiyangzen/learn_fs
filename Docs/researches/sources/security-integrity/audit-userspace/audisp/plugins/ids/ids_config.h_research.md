# sources/security-integrity/audit-userspace/audisp/plugins/ids/ids_config.h

Purpose: declares the IDS configuration ABI and bitmask values for every supported automated reaction.

Important APIs and data: defines `REACTION_*` flags for ignore/log/email, process/session termination, account actions, address blocking, and system-level termination. Declares `struct ids_conf`, `extern struct ids_conf config`, and config lifecycle functions.

Control flow: no executable flow; this header is included by config parsing, models, and reaction execution code.

State and persistence: `struct ids_conf` is process-local state, with no persistence contract beyond rereading `/etc/audit/ids.conf`.

Dependencies and integration: used by `ids_config.c`, `model_bad_event.c`, `model_behavior.c`, `origin.c`, `session.c`, `reactions.c`, and timer services. Reaction bits are iterated by `do_reaction`, so each flag must remain a unique single-bit value.

Risks: comments list planned but unimplemented defenses, which can be mistaken for available behavior. Adding flags beyond bit 31 would require auditing `do_reaction`'s 32-bit loop.

Test signals: compile-time consumers validate structure layout and constants; runtime tests should confirm each configured reaction string maps to the intended bit.
