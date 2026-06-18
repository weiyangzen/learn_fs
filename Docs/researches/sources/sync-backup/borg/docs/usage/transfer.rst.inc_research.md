# sources/sync-backup/borg/docs/usage/transfer.rst.inc

Purpose: Documents `borg transfer`, which copies archives from one repository to another and can upgrade, recompress, or rechunk data during the transfer.

Important APIs/types/functions: CLI contract is `borg [common options] transfer [options]`. Key options are `--dry-run`, `--other-repo SRC_REPOSITORY`, `--from-borg1`, `--upgrader UPGRADER`, `--compression`, `--recompress MODE` (`always` or `never`), `--chunker-params`, and archive filters.

Control flow: Runtime opens destination and source repositories, selects archives, optionally uses Borg 1 compatibility, optionally upgrades data, decides whether to reuse compressed chunks or recompress them, optionally rechunks, and writes missing archives to the destination. Dry-run checks intended work without mutation.

State and persistence: Mutates the destination repository by adding archives/chunks. The source repository should be read-only. Related repositories created with `repo-create --other-repo` preserve key material needed for deduplication and chunk ID compatibility.

Dependencies and integration points: Integrates with `repo-create --other-repo`, legacy Borg 1 support, compression and chunker modules, archive filters, and generated transfer-upgrade test data.

Risks: Wrong compression option spelling in examples/docs would confuse users; the help text mentions both `--compression` and prose `--compress`. Rechunking/recompression can be CPU and space intensive. Missing related key material can reduce deduplication or prevent compatible transfer.

Test signals: Cover dry-run idempotence, Borg 2 related repository transfer, Borg 1 `--from-borg1`, upgrader selection, recompress `never` vs `always`, chunker changes, filtered transfers, and repeated dry-run after completion.
