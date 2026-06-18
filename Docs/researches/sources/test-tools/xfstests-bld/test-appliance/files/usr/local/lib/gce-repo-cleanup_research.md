# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-repo-cleanup

Purpose: periodic cleaner for cached KCS Git repositories on `/cache`.

Important flow: exit if `/cache/repositories` is absent, wait while `/run/kernel-building` exists, update `linux.reference` weekly with `git fetch --all`, run `git gc --auto`, remove non-reference repos whose `last-used` is older than 30 days, clean active repos weekly with `git clean -xf -e /last-*`, and trim `/cache`.

State and dependencies: uses marker files `last-fetch`, `last-used`, and `last-touched`; deletes repository directories; calls `fstrim`. Depends on Git and GNU `find` mtime behavior.

Integration points: aligned with `util/git` repository storage under `/cache/repositories`; should not run while builds are active.

Risks and test signals: `rm -rf` of stale repos is destructive, so correctness depends on marker maintenance elsewhere. Weekly `git clean` may remove untracked build artifacts except last markers. Tests should create fake repo directories with marker mtimes and assert cleanup decisions.
