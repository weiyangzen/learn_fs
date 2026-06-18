# sources/sync-backup/rsync/testsuite/unsafe-byname_test.py

Purpose: direct behavioral test for `unsafe_symlink()` through the `t_unsafe` helper, using crafted symlink targets and current-directory paths.

Important APIs and flow: builds a table of `(link_target, curdir, expected)` cases and runs `TOOLDIR/t_unsafe target curdir` for each. Cases cover plain relative links, absolute and protocol-like double-slash paths, `..` escapes, repeated slashes, interior `dir/..` forms, empty targets, Vladimir Michl unsafe-links examples, and absolute current-directory forms based on the process CWD.

State and persistence: no fixture tree is required; the helper evaluates path strings. The test uses the current working directory exactly as the shell version did.

Dependencies and integration: targets `util1.c::unsafe_symlink()` and its path-depth model. Risks are CWD assumptions and helper output contract (`safe` or `unsafe`). Test signal is aggregated mismatch reporting after all cases, making it easier to see every rule regression in one run.
