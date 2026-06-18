# Research: sources/object-store/minio-mc/cmd/main.go

## sources/object-store/minio-mc/cmd/main.go

Purpose: this is the primary `mc` CLI bootstrap. It wires global flags, help rendering, profiling, configuration initialization, update checks, command registration, shell completion, and pager handling before dispatching to subcommands through `github.com/minio/cli`.

Important APIs and functions: `Main(args []string)` is the external entrypoint; `registerApp` builds the `cli.App`; `registerBefore` performs global setup; `initMC`, `migrate`, and `checkConfig` prepare and validate persisted client state; `commandNotFound` and `onUsageError` provide UX; `installAutoCompletion` integrates with `posener/complete`; `printMCVersion` overrides version output.

Control flow: `Main` handles completion mode, optional `MC_PROFILER`, probe metadata, terminal sizing, signal trapping, pager setup, and then runs the registered app. `registerApp` installs app-level action behavior for update checks, autocompletion, empty command help, and unknown-command suggestions. Every command is listed in `appCmds` and shares global flags.

State and persistence: reads `MC_CONFIG_FILE`, migrates config/share files, creates config/certs/CA directories, loads roots, and writes initial config if absent. It also stores profiler files under the mc profile directory and uses package globals for quiet/json/terminal/pager state.

Dependencies and integration: integrates all command files via `appCmds`, certificate/config helpers, probe metadata, terminal detection, MinIO update metadata, and trie/word-distance command suggestions.

Risks: `syscall.SIGKILL` cannot be trapped on Unix, but is passed to `trapSignals`; update checks run on normal command invocation; completion installation uses shell detection and rc-file modification; many setup failures terminate with `fatalIf`, which makes embedded use harder. Test coverage in this subset only indirectly exercises config helpers through `mc_test.go`.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/main.go -->
