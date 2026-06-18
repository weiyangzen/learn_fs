<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/fio.go -->
# sources/sync-backup/kopia/tests/tools/fio/fio.go

This file wraps execution of FIO either as a local executable or Docker image. `Runner` stores executable details, data directories, global FIO config, debug flag, and a path locker. Environment keys select local FIO, Docker image, local data root, and host data root.

`NewRunner` creates a temp data dir, chooses local or Docker execution, builds global write options, initializes a no-op path locker, and validates setup by writing test files. `verifySetupWithTestWrites` writes a small random test workload and verifies count/size. `RunConfigs` and `argsFromConfigs` translate config/jobs/options to FIO CLI args. `Run` executes the command and captures stdout/stderr. `Cleanup` removes the local data dir.

State includes temp filesystem data and Docker volume mapping. Dependencies are FIO/Docker availability and `pathlock`. Risks include environment-driven skip/failure, local/container path mismatches, no command timeout, direct I/O assumptions, and validation doing real writes. Tests cover local/docker runner paths when env is configured.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/fio.go -->
