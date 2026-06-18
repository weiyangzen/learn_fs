# sources/test-tools/unionmount-testsuite/Makefile

Purpose: minimal make entrypoint for the Python unionmount testsuite.

Important APIs/types/functions: `all` target prints `Nothing to do`; `clean` removes editor backup files in the root and `tests/`.

Control flow: there is no build. The suite is run through the `run` script, so make only provides a harmless default target and cleanup.

State and persistence: `clean` deletes `*~` and `tests/*~`; `all` writes only to stdout.

Dependencies and integration: depends on make and the shell `$(RM)` variable. Integrates with standard source-tree cleanup workflows.

Risks: cleanup is intentionally narrow and does not remove mounts, generated lower/upper trees, or Python caches.

Test signals: executing `make` should not alter the suite; `make clean` should remove only backup files.
