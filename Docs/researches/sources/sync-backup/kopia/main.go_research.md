<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/main.go -->
# sources/sync-backup/kopia/main.go

- Purpose: Main entrypoint for the Kopia CLI.
- Important APIs/types/functions: `usageTemplate`, `main`.
- Control flow: Constructs the CLI app and kingpin application, installs version/build strings, attaches logfile flags, configures error/usage writers and custom usage template, attaches commands, and parses `os.Args[1:]`.
- State and persistence: Process-level CLI configuration only; persistent effects are delegated to invoked commands.
- Dependencies and integration points: Integrates `cli`, `internal/logfile`, `repo` build metadata, and `kingpin`.
- Risks and edge cases: Usage template is a compatibility surface with kingpin templates and command metadata.
- Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/main.go -->
