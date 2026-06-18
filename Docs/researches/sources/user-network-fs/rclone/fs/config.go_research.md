# sources/user-network-fs/rclone/fs/config.go

Purpose: defines rclone's global filesystem configuration model, option metadata, config context helpers, reload validation, and environment-variable naming helpers.

Important APIs/types/functions: package globals include `globalConfig`, config-file function hooks (`ConfigFileGet`, `ConfigFileSet`, `ConfigFileHasSection`), `CountError`, `ConfigProvider`, and `ConfigEdit`. `ConfigOptionsInfo` is the large registry of global options and defaults. `ConfigInfo` is the typed runtime config struct with `config` tags. Key functions/methods include `init`, `(*ConfigInfo).Reload`, `InitialLogLevel`, `TimeoutOrInfinite`, `GetConfig`, `CopyConfig`, `AddConfig`, `ConfigToEnv`, and `OptionToEnv`.

Control flow: `init` sets nonzero defaults, registers `ConfigOptionsInfo` against `globalConfig`, and initializes a preliminary log level from command-line/env arguments. `Reload` applies derived behavior and validation: dump implies debug logging, dry-run/interactive raise stats visibility, compare/copy dest conflict is rejected, stats-one-line date settings imply parent flags, partial suffix length is bounded, retries/transfers/checkers are forced positive, stats unit defaults to bytes on invalid input, and logging reload hook is invoked. `InitialLogLevel` scans `os.Args` for verbose/debug forms and `RCLONE_LOG_LEVEL=DEBUG`.

State and persistence behavior: `globalConfig` is process-wide default state. `AddConfig` makes a shallow mutable copy stored in context, while `CopyConfig` propagates config and rc request markers into another context. Config persistence itself is decoupled through function pointers installed by `fs/config`.

Dependencies and integration points: central to all packages that call `fs.GetConfig`, register global options, create remotes, or parse CLI flags. Depends on option registration infrastructure, logging, network types, and many custom flag types (`BwTimetable`, `DumpFlags`, `SizeSuffix`, `Duration`, etc.).

Risks: `ConfigOptionsInfo` and `ConfigInfo` tags must stay synchronized; missing tags or default mismatches can break CLI/config loading. `AddConfig` is shallow, so slice/map pointer fields may share backing data. `InitialLogLevel` intentionally does a manual early parse and may not understand every pflag spelling.

Test signals: no direct tests in the listed file set, but many downstream configflags/configstruct tests and general rclone tests depend on this metadata and reload behavior.
