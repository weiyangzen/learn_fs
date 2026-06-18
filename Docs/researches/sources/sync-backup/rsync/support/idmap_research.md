<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/idmap -->
# sources/sync-backup/rsync/support/idmap

Purpose: generate rsync `--usermap` or `--groupmap` strings from passwd/group-style files for local transfers involving mounted backups with different UID/GID assignments.

Important APIs/types/functions: `NAME_ID_RE` parses `name:...:id` records. `main()` reads one or more files via `fileinput` and emits comma-separated mapping pairs. Argparse requires exactly one of `--from` or `--to`.

Control flow: scan each input line, skip non-matching records, build `name:id` pairs for `--to` or `id:name` pairs for `--from`, and print the comma-joined result.

State and persistence behavior: no persistent state or filesystem mutation; output is a command-line fragment for rsync.

Dependencies and integration points: depends on Python 3 and passwd/group file syntax. The output plugs directly into rsync `--usermap` or `--groupmap`.

Risks: the regex only accepts word-character names, so names with dashes or other valid system characters are skipped. Large mapping files can produce very long command lines. It does not validate duplicate names/IDs or local availability.

Test signals: fixture passwd and group files should cover `--from`, `--to`, skipped malformed lines, numeric IDs, and names outside `\w+` if behavior needs to be documented.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/idmap -->
