## sources/sync-backup/restic/internal/global/global_debug.go

Purpose: build-tagged debug/profile support for restic CLI commands.

Important APIs/types: `RegisterProfiling` wraps a Cobra command's `PersistentPreRunE`, starts profiling, registers `cobra.OnFinalize` to stop it, and adds profiling flags. `Profiler` stores selected options and a stop handle. `ProfileOptions` defines HTTP pprof listener, memory/CPU/trace/block profile paths, and insecure KDF toggle. `ProfileOptions.AddFlags` registers debug flags. `Profiler.Start` starts optional pprof HTTP server, enforces only one active file profile, starts `pkg/profile`, and applies low-security KDF settings when requested. `Profiler.Stop` stops the active profile.

Control flow and state: profiling starts after any original pre-run logic succeeds. Stop is global via Cobra finalization instead of per-command post-run. `insecure-kdf` mutates repository test KDF settings and is available only in debug/profile builds.

Dependencies and integration points: imports `net/http/pprof` side effects, `github.com/pkg/profile`, Cobra, pflag, repository test KDF hooks, and restic errors.

Risks and test signals: starting an unauthenticated pprof listener is explicitly debug-only but still security-sensitive. Multiple profile outputs are rejected to avoid conflicting profiler modes. This file has no direct tests in the target set; behavior is build-tag dependent.
