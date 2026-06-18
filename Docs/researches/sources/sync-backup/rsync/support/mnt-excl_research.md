<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/mnt-excl -->
# sources/sync-backup/rsync/support/mnt-excl

Purpose: generate rsync exclude rules for mount points under a source path, catching bind mounts that `--one-file-system` may not distinguish.

Important APIs/types/functions: `main()` normalizes the requested path and scans `MNT_FILE = /proc/mounts`.

Control flow: preserve whether the input path was slash-content style, resolve the path with `realpath()`, derive the parent/trailing anchor used by rsync filters, read mount paths from `/proc/mounts`, and print `- /relative/mount` for each mount beneath but not equal to the requested root.

State and persistence behavior: no mutation; emits exclude rules on stdout.

Dependencies and integration points: Linux-specific `/proc/mounts`, Python 3, and rsync exclude/filter syntax. Intended usage is piping into `rsync --exclude-from=-`.

Risks: mount paths with spaces are escaped in `/proc/mounts`; the script blindly uses `line.split()[1]`, so unusual escaping may not decode as users expect. It is Linux-centric. Realpath normalization changes symlinked source semantics.

Test signals: mock or fixture `/proc/mounts` behavior is hard-coded, so integration tests on a temporary mount namespace are most realistic. Validate differences between `/dir` and `/dir/` anchoring.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/mnt-excl -->
