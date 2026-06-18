# sources/security-integrity/audit-userspace/audisp/plugins/ids/reactions.h

Purpose: declares executable IDS reaction functions.

Important APIs and data: exposes individual process, session, account, address, and system reaction calls plus `do_reaction(unsigned int answer, const char *reason)`.

Control flow: no header flow; `do_reaction` interprets `REACTION_*` bitmasks.

State and persistence: declared functions may mutate OS state, firewall state, accounts, and process-local IDS state.

Dependencies and integration: consumers must include a `pid_t` definition before using `kill_process`; implementation integrates with `ids_config.h` constants.

Risks: signatures do not communicate side-effect severity or required privileges.

Test signals: compile-time coverage and mocked reaction dispatch by bitmask.
