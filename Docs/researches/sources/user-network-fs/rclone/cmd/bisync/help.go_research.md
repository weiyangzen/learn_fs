# sources/user-network-fs/rclone/cmd/bisync/help.go

Purpose: Build-tagged generator for `rc.md`, the embedded remote-control help text for the bisync RC endpoint.

Important APIs/types/functions: `main` writes generated help to stdout or a named file. `RcHelp` returns word-wrapped RC documentation. `toCamel` converts CLI flag names to RC parameter names. `GenerateParams` locates the cobra `bisync` command and emits non-hidden flags with type and usage.

Control flow: `go generate ./cmd/bisync` runs this file via the directive in `rc.go`. It writes a generated-file warning, static required `path1`/`path2`/`dryRun` docs, generated flag parameter lines, and links to command/manual docs.

State and persistence behavior: The only persistent output is the generated `rc.md` file when a path argument is supplied. It does not run in normal builds because of `//go:build none`.

Dependencies and integration points: Imports the real `cmd` and `bisync` packages so generated help reflects registered cobra flags. Uses `muesli/reflow/wordwrap`, pflag, and Go text casing.

Risks: Generated RC docs can drift if `go generate` is not run after flag changes. `toCamel` is simple hyphen splitting and assumes lowercase CLI flag names. Importing the command package during generation relies on init side effects registering `bisync`.

Test signals: `go generate ./cmd/bisync` followed by a diff of `rc.md` is the primary signal. New flags should appear in generated help unless hidden; hidden debug/localtime flags should not.
