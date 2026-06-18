# File Research: sources/os/plan9/9front/sys/src/cmd/git/diff

rc script for showing git working-tree diffs.

Key responsibilities:
- Parses commit base, summarize, and uncommitted options.
- Uses `git/walk` to list changed paths or summarize changes.
- Mounts scratch namespaces and binds commit tree as `a` and working tree as `b`.
- Runs `diff -u` for each changed file, using `/dev/null` for additions/deletions.

Important behavior:
- Default base commit is `HEAD`.
- `-u` includes uncommitted state in the walk filter.
- Path arguments are cleaned relative to the git root.

Notable risks:
- Output header says `diff <commit> uncommitted` once per run.
