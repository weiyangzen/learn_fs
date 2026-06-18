<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/file-attr-restore -->
# sources/sync-backup/rsync/support/file-attr-restore

Purpose: Perl utility that parses `find ... -ls` output and restores selected permissions, owners, and groups onto matching local filesystem objects.

Important APIs/types/functions: option parsing via `Getopt::Long`; main input loop; `parse_map_file()` for `user FROM TO` and `group FROM TO` mappings; `usage()`. Options include `--all`, `--perms`, `--owner`, `--groups`, `--map`, `--dry-run`, and repeated `--verbose`.

Control flow: parse options, optionally load user/group mapping overrides, compile a detailed regex for `find -ls` lines, decode find-style escaped filenames, check that the current local object type matches the recorded type, compute mode bits including setuid/setgid/sticky bits from the permission string, resolve owner/group names or numeric IDs with caching, and conditionally call `chmod()` and `chown()`. It prints changed attributes or verbose OK/skip messages.

State and persistence behavior: can mutate file modes and ownership for regular files, directories, devices, FIFOs, and sockets. It skips symlinks. Dry-run computes and reports changes without applying them.

Dependencies and integration points: depends on Perl, `Getopt::Long`, local passwd/group databases, and the exact format produced by `find -ls`. It complements rsync backup/restore workflows when attributes were captured as text.

Risks: parsing is format-sensitive and locale/date-output sensitive. Chowning can clear setuid/setgid bits, so the script repeats chmod after chown when high bits are set. Input filenames must be properly escaped; malformed input aborts. Running with owner/group restoration requires privileges and may map names unexpectedly without a map file.

Test signals: feed fixture `find -ls` lines for each supported file type, escaped names, mapping-file overrides, missing files, type mismatches, dry-run mode, and setuid/setgid preservation after chown.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/file-attr-restore -->
