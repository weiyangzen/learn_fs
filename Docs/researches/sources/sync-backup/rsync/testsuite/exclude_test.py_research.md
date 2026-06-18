## sources/sync-backup/rsync/testsuite/exclude_test.py

Purpose: broad regression suite for excludes, includes, filter rules, merge files, CVS exclusions, delete timing, prune-empty behavior, update output, and the `exclude-lsh` remote-shell variant.

Important APIs and control flow: detects `lsh` in the script name and configures `RSYNC_RSH`, `--rsync-path`, and host prefixes. It builds a complex `FROMDIR` tree with `.filt`, `.filt2`, `.cvsignore`, wildcard-sensitive file names, update fixtures, and expected `CHKDIR` state. It runs a sequence of `run_rsync`, `checkit`, `verify_dirs`, and `checkdiff` calls, mutating `CHKDIR` between cases to model expected filtered output. `run_with_stdin_filter()` feeds a materialized merge filter file on stdin.

State and dependencies: sets `CVSIGNORE`, uses `FROMDIR`, `TODIR`, `CHKDIR`, `SCRATCHDIR`, and optional local remote-shell support. It imports `cp_touch` and `verify_dirs` mid-file for fixture adjustment.

Integration points: exercises filter parser ordering, per-directory merge filters, side-specific rules, delete modes, relative mode interaction, and itemized update output.

Risks and test signals: high value but stateful. Risks include stale expected-tree mutations, timing sensitivity around directory mtimes, and push/pull ordering differences. Signals include exact tree comparisons after each major filter phase and exact `--update --info=skip` itemize output.
