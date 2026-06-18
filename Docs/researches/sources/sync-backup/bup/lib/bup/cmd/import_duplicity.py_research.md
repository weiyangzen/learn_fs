# sources/sync-backup/bup/lib/bup/cmd/import_duplicity.py

## Purpose
`import_duplicity.py` imports duplicity backup history into a bup save branch by restoring each duplicity collection timestamp into a temporary directory, indexing it, and saving it with matching commit dates.

## APIs and Control Flow
`logcmd` and `exc` log commands and skip execution under `--dry-run`. `main(argv)` validates source URL and destination save name, checks the bup repository, creates a temporary work directory, runs `duplicity collection-status`, parses `full` and `inc` timestamp lines from the log, then for each timestamp runs duplicity restore, `bup index -uxf`, and `bup save --strip --date ... -f ... -n ...`. Cleanup removes the tempdir in `finally`.

## State, Dependencies, Integration, Risks, Tests
It writes temporary duplicity cache, restore, index, and log files, then appends commits to the destination branch. Dependencies are external `duplicity`, `rm`, the current bup executable, `git.check_repo_or_die`, and timestamp parsing via `timegm/strptime`. Risks include experimental status, shell command failures aborting via `check_call`, fragile parsing of duplicity output, and `finally` cleanup being skipped in dry-run semantics only through `exc`. Test signals include dry-run logging, timestamp extraction, command sequence order, cleanup behavior, and date preservation in saved commits.
