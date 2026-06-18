# Research: sources/sync-backup/syncthing/script/commit-msg.go

## sources/sync-backup/syncthing/script/commit-msg.go

Purpose: Git hook/helper validating Syncthing commit subject style.

Important APIs/functions: regexp `subject = ^[\w/,\. ]+: \w`; constants `exitSuccess` and `exitError`; `main` reads one filename argument and checks the first line.

Control flow: validates argument count, reads the commit message file, splits by newline, tests the subject line, prints a diagnostic with the expected pattern on failure, and exits with status 1.

State and persistence: read-only access to the commit message file.

Dependencies and integration: standard library only; intended for Git commit-msg hook use. Risks include narrow allowed tag characters, no empty-file guard before `lines[0]`, and style-only enforcement. Test signal is hook exit code.
