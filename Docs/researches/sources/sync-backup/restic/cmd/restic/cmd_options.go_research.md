# sources/sync-backup/restic/cmd/restic/cmd_options.go

Purpose: implements `restic options`, printing the list of extended options.

Important APIs/types/functions: `newOptionsCommand`; inline `Run` handler; `options.List`.

Control flow and state: command prints a header, computes the maximum `namespace.name` width, then prints each extended option with aligned name and description. It does not open a repository or mutate state.

Dependencies and integration points: depends on `internal/options` as the source of available extended options and `globalOptions.Term.Print` for output.

Risks: output order and alignment depend on `options.List`. There is no JSON mode handling; it is plain text.

Test signals: root flag parsing tests cover command construction; no direct output test in this shard.
