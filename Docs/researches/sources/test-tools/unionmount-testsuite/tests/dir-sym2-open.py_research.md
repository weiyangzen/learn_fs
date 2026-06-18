# sources/test-tools/unionmount-testsuite/tests/dir-sym2-open.py

Purpose: tests open behavior through an indirect symlink chain that resolves to an existing directory.

Important APIs/types/functions: five `subtest_*` functions using `ctx.indirect_dir_sym` and `ctx.open_file`.

Control flow: read-only open through the indirect symlink succeeds twice. Write-like modes (`O_WRONLY`, append, `O_RDWR`, append/read-write) expect `EISDIR`, then read-only open confirms the target remains accessible.

State and persistence: no intended mutation of either symlink or target directory.

Dependencies and integration: relies on setup-created direct and indirect directory symlinks and recursive symlink handling in `context.pathwalk`.

Risks: symlink-loop protection and terminal slash handling can alter expected errors if pathwalk diverges from kernel behavior.

Test signals: catches regressions in multi-hop symlink resolution over overlay layers.
