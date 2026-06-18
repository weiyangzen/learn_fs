# sources/sync-backup/borg/docs/usage/benchmark_crud.rst.inc

Purpose: generated reference for `borg benchmark crud`, which measures create, read/extract, update, and delete behavior against a repository.

Important APIs and control flow: requires a `PATH` for generated input data and an existing repository from common `--repo` handling. `--json-lines` switches output to JSON Lines. The benchmark creates artificial zero and random datasets, archives them, dry-run extracts, repeats unchanged creates to measure files-cache behavior, and deletes/compacts.

State and persistence: writes about 1 GB of benchmark input data plus repository objects and temporary benchmark archives named `borg-benchmark-crud*`.

Dependencies and integration points: depends on repository initialization, encryption passphrase automation via `BORG_PASSPHRASE`, files cache, extract dry-run, delete, and compaction paths.

Risks: consumes substantial disk space and uses artificial data, so results may not reflect real workloads. Running on a non-idle machine or network repository can skew measurements.

Test signals: verify command refuses missing repo/path, emits valid JSON Lines, cleans up benchmark archives, and measures all C/R/U/D phases.
