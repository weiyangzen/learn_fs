# sources/test-tools/unionmount-testsuite/tests/dir-sym2-weird-open.py

Purpose: verifies indirect directory symlink error behavior with create, exclusive, and truncate flags.

Important APIs/types/functions: ten `subtest_*` functions using `ctx.indirect_dir_sym` and `ctx.open_file`.

Control flow: combinations of read/write access with `O_CREAT`, `O_TRUNC`, and both generally expect `EISDIR`; combinations including `O_CREAT|O_EXCL` expect `EEXIST`. After each failed operation the symlink is opened read-only to confirm the directory still resolves.

State and persistence: no files should be created and no directory data should be copied up or changed by failed opens.

Dependencies and integration: depends on context symlink-chain tracking and open flag/error modeling.

Risks: error precedence for indirect symlinks plus terminal slashes is a frequent kernel compatibility edge.

Test signals: validates multi-hop symlink-to-directory behavior under unusual open flags.
