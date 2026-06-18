# Research: sources/object-store/minio-mc/cmd/quota-main.go

## sources/object-store/minio-mc/cmd/quota-main.go

Purpose: groups bucket quota subcommands under `mc quota`.

Important APIs and variables: `quotaSubcommands` lists `set`, `info`, and `clear`; `quotaCmd` defines the parent command; `mainQuota` handles parent invocation.

Control flow: invoking the parent without a valid subcommand delegates to `commandNotFound`, which can suggest closest subcommands or fail with a global error.

State and persistence: parent command itself performs no remote mutation; subcommands do.

Dependencies and integration: registered in `appCmds` from `main.go` and shares global flags/setup. It depends on subcommand variables defined in sibling quota files.

Risks and tests: no custom help template in this file, so parent UX depends on default CLI behavior plus `commandNotFound`. No direct tests.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/quota-main.go -->
