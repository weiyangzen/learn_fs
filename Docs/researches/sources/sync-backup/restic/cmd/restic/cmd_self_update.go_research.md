# sources/sync-backup/restic/cmd/restic/cmd_self_update.go

Purpose: build-tagged implementation of `restic self-update`, downloading and replacing the restic binary when built with `selfupdate`.

Important APIs/types/functions: `registerSelfUpdateCommand`; `SelfUpdateOptions`; `runSelfUpdate`.

Control flow and state: if `--output` is absent, resolves the current executable. It validates that an existing output is a regular file or that the parent directory exists and is a directory, prints the target path, then calls `selfupdate.DownloadLatestStableRelease` with the current version and progress callback. Persistent state is the downloaded binary at the output path, potentially replacing the running executable.

Dependencies and integration points: uses `internal/selfupdate`, `os.Executable`, filesystem stat checks, and progress printer. Build tag `selfupdate` controls availability.

Risks: replacing the running binary is platform-sensitive. Output path validation avoids writing to directories or non-regular files but does not create missing parent directories. Network/signature behavior is delegated to `selfupdate`.

Test signals: no direct test in this shard; build-tag coverage and selfupdate package tests are expected.
