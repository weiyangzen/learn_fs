## sources/sync-backup/bup/lib/cmd/bup-import-rdiff-backup

Purpose: imports an rdiff-backup repository into a Bup branch by restoring each increment to a temporary directory and saving it with the original timestamp.

Important APIs and control flow: the shell script supports `-n/--dry-run`, validates two arguments, lists increments using `rdiff-backup --list-increments --parsable-output`, then loops through `timestamp type` lines. Each iteration creates a temp restore directory, runs `rdiff-backup -r timestamp`, indexes with a temporary index file, and saves with `bup save --strip --date=timestamp -n branch`.

State and dependencies: creates temporary restore dirs and index files in the current directory, and writes Bup repo objects/refs through `bup index` and `bup save`. It depends on GNU-ish `date -d @timestamp`, `mktemp`, `rdiff-backup`, and the colocated `bup` executable.

Risks and tests: cleanup is manual per successful iteration; failures before `rm -rf` can leave temp directories or temp index names. Timestamp parsing and `date -d` are portability risks. `test-import-rdiff-backup` skips when `rdiff-backup` is unavailable and verifies imported save count and latest contents against `Documentation`.
