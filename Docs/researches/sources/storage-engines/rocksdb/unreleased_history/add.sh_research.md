# sources/storage-engines/rocksdb/unreleased_history/add.sh

## Purpose

Interactive helper for adding a new unreleased RocksDB release-note fragment in the correct category and staging it in git.

## Important APIs, Control Flow, And Dependencies

The script prints release note advice and markdown formatting examples. If a target path is provided as `$1`, it uses that directly after prompting for return. Otherwise it lists one-level directories under `unreleased_history/`, asks the user to choose a group by number, prompts for a file name, replaces spaces with underscores, opens the target with `${EDITOR:-nano}`, and runs `git add "$TARGET"`.

## State, Persistence, Integration, Risks, And Test Signals

Persistent state is the created or edited release-note file and the git index entry. It depends on a shell, `find`, `grep`, `head`, `tail`, `tr`, an editor, and git. Risks include interactive input ambiguity, no validation that a numbered selection is in range, and automatic `git add` even if the edit is incomplete. The script's success signal is zero exit after the file is edited and staged.
