# sources/security-integrity/libcap/progs/getpcaps.c

Purpose: displays capability state for one or more process IDs.

Important APIs/functions: parses long-form options `--help`, `--verbose`, `--ugly`/`--legacy`, `--iab`, and `--license`. For each PID, it uses `cap_get_pid()`, `cap_to_text()`, and optionally `cap_iab_get_pid()`/`cap_iab_to_text()` to print process capability and IAB state.

Control flow: arguments are processed sequentially; options update local output mode and PID tokens are parsed with `strtol()` with overflow and trailing-character checks.

State and dependencies: no persistent state. Depends on libcap's process capability APIs and `/proc`/kernel support.

Risks and test signals: process disappearance and permission failures produce nonzero exit status. Legacy format support is preserved for old scripts. `quicktest.sh` uses it to verify shell scripts do not unexpectedly receive file capabilities.
