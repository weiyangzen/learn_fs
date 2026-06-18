# sources/test-tools/crashmonkey/code/tests/generic_335.cpp

Purpose: xfstests generic/335 reproduction for directory rename plus sibling creation. It moves `A/B/foo` to `C/foo`, creates `A/bar`, fsyncs `A`, and checks both names are in their expected directories after recovery.

Important APIs/types/functions: `Generic335`, `mkdir`, `open`, `rename`, `fsync` on directory fd, `Checkpoint`, `opendir`/`readdir`, and `DataTestResult`.

Control flow: setup creates `A/B`, `C`, and `A/B/foo`, then syncs. Run renames `foo` from `A/B` into `C`, creates `A/bar`, fsyncs directory `A`, and checkpoints. Check enumerates `A`, `A/B`, and `C` to validate placement.

State/persistence behavior: after checkpoint 1, `foo` must be only in `C`, `bar` only in `A`, and `A/B` should not retain stale entries.

Dependencies/integration: uses `mnt_dir_`, raw directory operations, and CrashMonkey checkpointing.

Risks/test signals: fsyncing `A` rather than all affected directories is the intended stress. Failures include missing `foo`, duplicate old/new locations, or `bar` in the wrong directory.
