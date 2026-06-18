# sources/sync-backup/rsync/testsuite/delete_test.py

Purpose: ported delete behavior coverage for dry-run output parity, `--remove-source-files`, and protect/exclude filter interaction with `--delete-excluded`.

Important APIs/types/functions: `hands_setup`, `_run_capture`, `_strip_chatter`, `checkit`, `rsync_argv`, `diff`, `makepath`, and `test_fail`.

Control flow: set up destination extras, capture output of a plain copy to `CHKDIR/copy`, capture output of `--del --dry-run` to `copy2`, strip chatter, and require output equality. Build `CHKDIR/empty` as directories-only source mirror. Run `--del --remove-source-files` and verify destination equals copy while source equals dirs-only mirror. Then create a per-dir filter file with `P foo` and `- bar`, plus excluded `baz`, run `--delete-excluded`, and verify protected foo survives while bar and baz are deleted.

State and persistence behavior: modifies both source and destination; remove-source-files should leave source files gone but directories present. Filter file state controls deletion.

Dependencies and integration points: delete dry-run output, source removal, filter protect/exclude semantics, and harness comparisons.

Risks and test signals: output comparison intentionally strips variable chatter. Failures identify user-visible dry-run drift, source cleanup bugs, or filter-protection errors.
