# sources/sync-backup/restic/cmd/restic/cmd_recover.go

Purpose: implements `restic recover`, creating a new snapshot from unreferenced tree roots found in raw repository data.

Important APIs/types/functions: `newRecoverCommand`; `runRecover`; `createSnapshot`.

Control flow and state: obtains hostname, opens exclusive lock, memoizes snapshot list, repairs index completeness, loads index, collects all tree blob IDs as potential roots, loads every tree and marks subtree references, marks snapshot root trees as referenced, then saves a synthetic tree containing one directory per unreferenced root. If roots exist, `createSnapshot` saves a `/recover` snapshot tagged `recovered`; otherwise it prints no snapshot to write.

Dependencies and integration points: uses `repository.RepairIndex`, `repo.ListBlobs`, `data.LoadTree`, `data.ForAllSnapshots`, `data.NewTreeWriter`, and `data.SaveSnapshot`.

Risks: tree load failures are logged and skipped, possibly leaving roots classified conservatively. Recovery can expose orphan data but cannot reconstruct original names above root boundaries. It mutates repository by writing tree and snapshot files.

Test signals: recover integration test forgets a snapshot, runs recover, checks one new snapshot exists, and verifies the old root tree is reachable.
