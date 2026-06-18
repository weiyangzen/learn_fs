# sources/test-tools/crashmonkey/code/tests/generic_104.cpp

Purpose: xfstests generic/104 reproduction. It creates `foo` and `bar`, adds hard links to both, fsyncs `bar`, and expects directory metadata to be clean enough for removal after recovery cleanup.

Important APIs/types/functions: `Generic104`, `link`, `open`, `fsync`, `Checkpoint`, `system("rm -f ...")`, `rmdir`, `errno`, and `DataTestResult`.

Control flow: `setup()` creates `test_dir_a/foo` and `bar`, closes them, and syncs. `run()` creates `foo_link_` and `bar_link_`, opens/fsyncs `bar`, and checkpoints. `check_test()` removes all visible entries in the directory and expects `rmdir` to succeed.

State/persistence behavior: link-count and directory-entry replay must not leave hidden references or stale index entries after cleanup.

Dependencies/integration: direct POSIX operations and CrashMonkey checkpointing; uses external shell `rm`.

Risks/test signals: the checker does not validate exact link counts, only cleanup consistency. Failure is `ENOTEMPTY` on directory removal.
