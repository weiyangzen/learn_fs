# sources/test-tools/unionmount-testsuite/tests/dir-sym1-weird-open.py

Purpose: exercises direct directory symlink opens with create, exclusive, and truncate flag combinations.

Important APIs/types/functions: ten `subtest_*` functions using `ctx.direct_dir_sym` and `ctx.open_file`.

Control flow: `O_CREAT` and `O_TRUNC` combinations through the symlink to a directory generally expect `EISDIR`, while `O_CREAT|O_EXCL` combinations expect `EEXIST`. Each subtest reopens the symlink read-only to confirm the target directory is unchanged.

State and persistence: failed operations should not create files, truncate anything, or copy up directory data unexpectedly.

Dependencies and integration: depends on `context.open_file` create/truncate/exclusive error prediction and setup-created direct dir symlink.

Risks: errno behavior is kernel-sensitive for `O_EXCL` plus symlinks and terminal slash paths.

Test signals: validates symlink-to-directory error precedence and post-failure stability.
