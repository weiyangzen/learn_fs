# sources/sync-backup/restic/cmd/restic/cmd_init.go

Purpose: implements `restic init`, creating a new repository with a selected repository format and optional chunker parameters copied from a secondary repository.

Important APIs/types/functions: `newInitCommand`; `InitOptions` embedding `global.SecondaryRepoOptions`; `runInit`; `maybeReadChunkerPolynomial`; `initSuccess` JSON output. Flags include `--repository-version`, `--copy-chunker-params`, and secondary repository options.

Control flow and state: `runInit` rejects positional arguments, parses version as `stable`, `latest`, empty, or numeric, optionally opens a secondary repository to read its chunker polynomial, then calls `global.CreateRepository`. It writes repository config, key, and layout through global repository creation. Text output strips repository passwords; JSON emits `message_type`, repository ID, and stripped repository location.

Dependencies and integration points: uses `restic.StableRepoVersion`, `restic.MaxRepoVersion`, `location.StripPassword`, `chunker.Pol`, and global backend/repository creation. Secondary repository handling integrates with copy workflows.

Risks: accepting numeric versions pushes validation into repository creation. Secondary repository options are rejected unless `--copy-chunker-params` is set, preventing accidental unintended reads. JSON/text output behavior diverges.

Test signals: integration test covers invalid secondary options, successful chunker parameter copying, and repository reopening.
