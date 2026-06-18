# sources/sync-backup/bup/dev/configure-sampledata

## Purpose
Creates or cleans versioned sample data used by bup tests and the make build.

## Important APIs, Types, and Functions
Supports `--setup`, `--clean`, and `--revision`; internal `revision=3`, `rm_symlinks`, and `clean`.

## Control Flow
`--setup` cleans legacy/sample data, creates `test/sampledata/var`, symlinks, FIFO, copied Python/docs content, optional randomized path zoo, and `rev/v3` marker. `--clean` removes generated var/legacy entries. `--revision` prints the revision.

## State and Persistence Behavior
Writes generated sampledata under `test/sampledata/var` and removes prior generated data. The revision marker is a make dependency.

## Dependencies and Integration Points
Called by `GNUmakefile all/clean`; uses `dev/make-random-paths` when randomized sample paths are enabled.

## Risks and Test Signals
Risks include stale sampledata after content shape changes without revision bump, platform FIFO/symlink support, and optional random path instability. Signals are existence of `rev/v3` and clean idempotence.
