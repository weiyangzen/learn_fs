# sources/security-integrity/audit-userspace/docs/check-manpages.sh

Purpose: POSIX shell test that validates every local manpage source with formatter warnings enabled.

Important behavior: Honors `MAN` and `srcdir` environment variables. Skips with exit 77 if `man` is unavailable, `C.UTF-8` locale is unavailable, or the `man` command lacks `--warnings`. For each `*.[0-9]` page it runs `man --warnings -E UTF-8 -l -Tutf8 -Z` with `LC_ALL=C.UTF-8`, empty `MANROFFSEQ`, and fixed `MANWIDTH=80`.

Control flow: Resolves `srcdir`, performs skip checks, loops over manpage files, captures stderr and exit status, prints failures, errors if no pages were found, and exits with aggregate failure state.

State and persistence: No persistent state. It only reads manpage files and emits diagnostics.

Dependencies and integration: Registered as an automake `TESTS` entry by `docs/Makefile.am`. Depends on a GNU/man-db style `man` with `--warnings`.

Risks: Environments without `C.UTF-8` or compatible `man` skip coverage. It treats any stderr as failure because `man` may return success despite formatter warnings. Shell glob `*.[0-9]` covers one-digit sections only, matching this tree's convention.

Test signals: Run directly from `docs` and from a VPATH build with `srcdir` set. Inject a malformed roff page to verify stderr causes failure.
