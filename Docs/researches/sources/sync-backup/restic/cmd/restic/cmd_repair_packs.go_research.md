# sources/sync-backup/restic/cmd/restic/cmd_repair_packs.go

Purpose: implements `restic repair packs`, salvaging intact blobs from specified damaged pack files.

Important APIs/types/functions: `newRepairPacksCommand`; `runRepairPacks`.

Control flow and state: parses each argument as a full restic ID into an ID set and rejects empty input. It opens an exclusive lock, loads the index, saves raw backup copies of each target pack into current working directory as `pack-<id>` with exclusive create, then calls `repository.RepairPacks`. It prints a follow-up hint to run `repair snapshots --forget`.

Dependencies and integration points: uses raw pack loading, local filesystem backup writes, repository pack repair, and index state.

Risks: backup files are written to the process CWD and fail if names already exist. If `LoadRaw` returns nil, the load error is returned. Full ID parsing rejects short IDs. Command mutates repository by removing/replacing damaged pack references.

Test signals: no direct integration test file in this shard, but repair snapshots tests create damaged pack scenarios after index rebuild.
