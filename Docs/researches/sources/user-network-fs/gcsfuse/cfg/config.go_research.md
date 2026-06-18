## sources/user-network-fs/gcsfuse/cfg/config.go

Purpose: Generated core configuration surface for gcsfuse. It defines optimization rules, machine groups, the full YAML-backed `Config` schema, command-line flag registration, Viper flag binding, and `Config.ApplyOptimizations`.

Important APIs/types/functions: `AllFlagOptimizationRules` maps config paths to profile/machine/bucket optimization rules. `machineTypeToGroupMap` maps high-performance GPU/TPU machine types to `high-performance`. `Config` and nested structs model cloud profiler, debug, dummy I/O, file cache, filesystem, GCS auth/connection/retries, list, logging, metadata cache, metrics, MRD, read, trace, workload insight, and write settings. `BuildFlagSet(*pflag.FlagSet)` registers defaults, hidden/deprecated flags, and help text. `BindFlags(*viper.Viper, *pflag.FlagSet)` maps CLI flags into hierarchical Viper keys. `ApplyOptimizations` mutates unset config values based on profile, machine type, and bucket type.

Control flow: optimization first exits when `DisableAutoconfig` is set, resolves machine type through `getMachineType`, then for each generated optimizable config path checks `v.IsSet` to preserve user values, calls `getOptimizedValue`, type-asserts the result, mutates the corresponding config field if changed, and records `OptimizationResult`. Flag construction is sequential and returns on any `MarkHidden`/`MarkDeprecated` error. Binding is a long ordered sequence of `v.BindPFlag` calls returning on first error.

State and persistence: `ApplyOptimizations` mutates the in-memory `Config`, including `MachineType`, and returns a map of optimized flags. Build/bind functions mutate provided flag/viper objects. No persistence is performed directly; callers serialize/use the resulting config elsewhere.

Dependencies and integration points: imports `cfg/shared`, `pflag`, `viper`, and `time`; depends on helpers in `optimize.go`, defaults in `config_util.go`, custom types in `types.go`, and validation/rationalization in neighboring cfg files. It is consumed by command startup and tests.

Risks: generated code is large and easy to desynchronize from templates/docs. `v.IsSet` governs user override preservation, so defaults or config-file sentinels must be handled carefully. Hidden/deprecated flags still bind into config and can affect behavior. Optimization type assertions silently skip mismatched rule values. Machine metadata lookup failure is non-fatal but disables machine-based optimization.

Test signals: `config_test.go` generated tests cover every optimizable flag for user-set preservation, no-op cases, profile/machine/bucket scenarios. `optimize_test.go` covers metadata lookup and hierarchical optimized flag formatting. CI excludes this generated file from Codecov.
