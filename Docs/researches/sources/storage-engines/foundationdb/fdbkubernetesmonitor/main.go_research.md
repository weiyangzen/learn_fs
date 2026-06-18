# sources/storage-engines/foundationdb/fdbkubernetesmonitor/main.go

Purpose: command entry point for `fdbkubernetesmonitor`. It supports launcher mode for supervising fdbserver, init mode for copying required binaries/libraries/config, and sidecar mode for version-dependent file copying plus idle signal wait.

Important APIs and functions: global flags define paths, mode, process count, pprof, node watch, TLS cert/key, and additional environment file. `initLogger` configures JSON zap logging with optional lumberjack rotation. `parseFlagsAndSetEnvDefaults` maps environment variables to flags. `main` parses flags, reads the version file, builds copy details, and dispatches by `executionMode`. `loadAdditionalEnvironment` parses `export KEY=value` lines.

Control flow: flags are registered first, environment defaults are applied before `pflag.Parse`, then current container version is read. Launcher mode loads additional env, parses the FDB version, creates a signal context, and calls `startMonitor`. Init mode copies files and exits. Sidecar mode copies only when its version differs from the main container version, then blocks until SIGINT/SIGTERM.

State and persistence behavior: writes log files when configured, copies files through `copyFiles`, and reads version/additional-env files. Launcher mode delegates pod annotation and process state to `monitor.go`.

Dependencies and integration points: integrates with copy helpers, `api.ParseFdbVersion`, monitor startup, zap/zapr logging, pflag, lumberjack, and OS signal handling.

Risks: environment defaults are applied before CLI parse, so malformed env values can abort flag parsing. `loadAdditionalEnvironment` tolerates unparsable lines by logging and continuing. Providing only one TLS file path reaches HTTPS setup and may fail later.

Test signals: no direct `main` tests in this subset; copy behavior, config parsing, and monitor subcomponents are tested separately.
