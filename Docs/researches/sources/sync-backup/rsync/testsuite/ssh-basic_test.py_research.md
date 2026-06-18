# sources/sync-backup/rsync/testsuite/ssh-basic_test.py

Purpose: basic remote-shell transfer coverage, using the test `lsh.sh` shim by default or real `ssh` when `rsync_enable_ssh_tests=yes`.

Important APIs and flow: imports `checkit`, `hands_setup`, `runtest`, paths, and skip helper. It probes `[SSH, -oBatchMode yes, localhost, echo, yes]`; if stdout is not exactly `yes`, the test skips. After `hands_setup()`, `_basic()` runs `checkit()` with `-avH -e SSH --rsync-path=RSYNC_PEER FROMDIR/ localhost:TODIR`. `_delete_after_rename()` renames destination `text` to `ThisShouldGo` and reruns with `--delete` to confirm remote deletion/update behavior.

State and persistence: uses the standard hands fixture tree, mutates `TODIR` between the two subtests, and relies on environment variable selection for real ssh.

Dependencies and integration: exercises remote-shell command construction, `--rsync-path`, hard-link preservation option plumbing, and delete pass behavior. Risks include localhost ssh authorization and multi-word rsync peer command quoting. Test signal comes from `checkit()` tree comparisons and `runtest()` failure propagation.
