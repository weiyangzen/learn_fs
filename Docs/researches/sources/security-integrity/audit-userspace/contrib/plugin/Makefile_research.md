# sources/security-integrity/audit-userspace/contrib/plugin/Makefile

Purpose: Minimal standalone build recipe for the older manual `audisp-example` plugin.

Important APIs and targets: Defines warning/debug `CFLAGS`, links with `-lauparse -laudit`, compiles `audisp-example.c`, and cleans the binary and object files.

Control flow: Single `gcc` invocation for `all`; simple file deletion for `clean`.

State and persistence: Produces the `audisp-example` executable in the contrib directory.

Dependencies and integration: Requires installed libaudit and libauparse development files. This is a contrib sample outside the main automake build.

Risks: No hardening, no dependency tracking, no include path control, and no installation handling. It may fail if local source headers differ from installed library headers.

Test signals: Run `make clean && make`, then feed raw audit logs to the executable and verify output from the manual event loop.
