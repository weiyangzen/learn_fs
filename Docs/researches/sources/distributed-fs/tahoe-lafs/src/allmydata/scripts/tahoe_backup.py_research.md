# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_backup.py

## Purpose
Implements `tahoe backup`, creating immutable, timestamped backups of a local directory tree under `ALIAS:TO/Archives/<timestamp>` and updating `ALIAS:TO/Latest`. It reuses prior file and directory caps through `backupdb`.

## APIs, Types, And Control Flow
`BackerUpper.run` opens `private/backupdb.sqlite`, resolves the destination alias, ensures the target `Archives` directory exists, collects backup targets deepest-first, runs `run_backup`, then links the completed root dircap into `Archives` and `Latest`. `collect_backup_targets` classifies files, directories, symlinks, special files, permission failures, and undecodable names. `FileTarget` uploads or reuses file caps; `DirectoryTarget` consumes accumulated child contents and creates or reuses immutable directories. `BackupProgress` tracks mutable progress counters and child maps; `BackupComplete.report` formats final output. HTTP helpers upload files with PUT `/uri`, create immutable directories with POST `?t=mkdir-immutable`, and link children with PUT `?t=uri`.

## State, Persistence, And Integration
Reads local filesystem metadata from `os.stat`, uploads file bytes to the gateway, writes backup cache records through `backupdb`, and mutates remote Tahoe directories. Metadata stored in created directory entries includes POSIX-ish stat fields when present. It integrates with CLI excludes from `BackupOptions`, `common_http`, alias parsing, Tahoe JSON byte encoding, and encoding utilities.

## Risks And Test Signals
Risks include trusting timestamp cache decisions, skipping symlinks/special files, memory use from materializing all targets, blocking uploads, partial remote state if linking `Archives` or `Latest` fails after upload, and returning rc 2 when skips occurred. Test signals include `allmydata/test/cli/test_backup.py`, backupdb tests, and web API tests for immutable directory creation/linking.
