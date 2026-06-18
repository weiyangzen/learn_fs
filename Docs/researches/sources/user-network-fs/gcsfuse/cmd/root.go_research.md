# sources/user-network-fs/gcsfuse/cmd/root.go

## Purpose
`root.go` builds and executes the gcsfuse Cobra root command. It owns the command-line/config-file pipeline that produces `mountInfo` and invokes a mount function. It also preserves legacy single-hyphen long flag compatibility by converting args before Cobra parses them.

## Important APIs And Types
`mountInfo` stores CLI flags for logging, explicit config-file flags, the final resolved `*cfg.Config`, optimized flags as a hierarchical map, and the Viper instance used for explicit-set checks. `mountFn` abstracts mounting for test injection. `getCliFlags` collects changed CLI flags while hiding internally added foreground in background mode. `getConfigFileFlags` reloads the config file into a fresh Viper to log only user-specified YAML. `newRootCmd(m mountFn) (*cobra.Command, error)` constructs the command. `convertToPosixArgs` rewrites single-hyphen long flags to double-hyphen form while preserving `-h` and `-v`. `ExecuteMountCmd` wires the real `Mount` function and exits fatally on setup/execution errors.

## Control Flow And State
`newRootCmd` creates a new Viper and config object, registers `--config-file`, builds all generated flags, and binds them. In `PersistentPreRunE`, it resolves and reads the config file if provided, unmarshals with YAML tags and `ErrorUnused`, validates, applies optimizations, rationalizes, collects CLI/config/optimized flag logs, and stores Viper in `mountInfo`. `RunE` calls `populateArgs` on positional args after the program name and then invokes the provided mount function. Command execution does not persist state by itself; it reads config files and records values in memory for logging and mount setup.

## Dependencies And Integration
The file depends on Cobra, pflag, Viper, mapstructure, cfg, common versioning, logger, and util path resolution. It is the top-level integration point for `params.yaml`, cfg custom decode hooks, validation, optimizations, rationalization, mount argument parsing in `legacy_main.go`, and final mount execution.

## Risks And Test Signals
Risks include command arity confusion because tests include the executable name in args, accidental acceptance/rejection changes from `ErrorUnused`, exact Viper key dependence, loss of legacy single-hyphen compatibility, and incorrect optimized flag logging if hierarchical map creation fails. Tests in `datatypes_parsing_test.go`, `config_validation_test.go`, and `config_rationalization_test.go` exercise most command setup paths, including help/version compatibility, data type parsing, config-file validation, defaults, and rationalization through the command pipeline.
