# sources/storage-engines/rocksdb/unreleased_history/release.sh

## Purpose

Release helper that folds categorized unreleased history fragments into `HISTORY.md` under a new version header derived from `include/rocksdb/version.h`.

## Important APIs, Control Flow, And Dependencies

The script requires the `unreleased_history/` directory. Unless `DRY_RUN` is set, it refuses to run with uncommitted changes under `unreleased_history/` or `HISTORY.md`. It writes `HISTORY.new` from the top of the existing history through the `NOTE` marker, appends a version/date header, then processes known directories in order: new features, public API changes, behavior changes, bug fixes, and performance improvements. `process_file` trims whitespace, ensures the first nonempty line starts with `* `, appends content to `HISTORY.new`, and removes the fragment with `git rm` unless in dry run. It checks for unexpected top-level entries, appends the remainder of existing history, and either diffs or replaces `HISTORY.md`.

## State, Persistence, Integration, Risks, And Test Signals

Persistent state includes `HISTORY.new`, the updated `HISTORY.md`, removed release-note fragments, and git index changes from `git rm`. Dependencies include awk, git, ls, find with GNU/BSD regex differences, uname, diff, and version macros in `include/rocksdb/version.h`. Risks include parsing `HISTORY.md` around the first `NOTE`, shell word splitting over filenames with spaces in release directories, category ordering being hard-coded, and requiring a clean working tree only for selected paths. `DRY_RUN=1` provides a non-mutating diff signal; normal success prints a revert command.
