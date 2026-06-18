# sources/test-tools/kdevops/scripts/infer_last_stable_kernel.sh

## Purpose
This shell helper infers a conservative recent stable Linux kernel tag from a local git object directory, intended as a default kernel reference for A/B testing.

## Important APIs, Types, And Functions
The script takes one optional argument, `GIT_TREE`, defaulting to `/mirror/linux.git`. It uses `git --git-dir="$GIT_TREE" tag --list`, `grep -v -- '-rc'`, `sort -V`, and `tail -2 | head -1`.

## Control Flow
If the git tree directory is missing, it emits `v6.12`. Otherwise it lists stable `v6.*` tags, excludes release candidates, sorts by version, and deliberately selects the second-to-last stable tag. If none exists, it repeats the process for `v5.*`. If still empty, it emits `v6.12`.

## State And Persistence
It reads only the local git repository metadata. It writes no files and prints the selected tag to stdout.

## Dependencies And Integration Points
It depends on `git`, `grep`, `sort -V`, `tail`, and `head`. Consumers likely use the emitted tag as a kdevops kernel version default.

## Risks And Test Signals
Choosing `tail -2 | head -1` means "previous stable", not the latest stable, which matches a conservative testing stance but conflicts with the file name if interpreted literally. Lightweight/malformed tags or an empty mirror can force fallback. Tests should create temporary bare repositories with v5/v6 and rc tags and assert the second-latest stable behavior and fallbacks.
