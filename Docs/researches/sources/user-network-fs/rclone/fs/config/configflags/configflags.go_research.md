# sources/user-network-fs/rclone/fs/config/configflags/configflags.go

Purpose: registers and applies global CLI flags that either map to `fs.ConfigOptionsInfo` or require special handling outside the generic config system.

Important APIs/functions: package globals store raw flag values such as verbosity, config/cache/temp dirs, delete mode booleans, bind address, disabled features, headers, metadata, and DSCP. `AddFlags(ci, flagSet)` registers generic options and special flags. `SetFlags(ci)` applies special flags to `fs.ConfigInfo`, config paths, and temp/cache dirs. `parseDSCP` maps numeric and named DSCP values to 6-bit codes.

Control flow: `AddFlags` delegates generic option registration to `flags.AddFlagsFromOptions`, then registers legacy/special flags. `SetFlags` folds obsolete dump flags into `ci.Dump`, resolves `-v`/`-q` conflicts with `--log-level`, chooses delete mode, resolves bind address to exactly one IP, parses disabled features/help, parses upload/download/general headers, parses lowercase metadata keys, shifts DSCP into traffic class bits, applies `--config`, `--cache-dir`, and `--temp-dir`, records whether `--multi-thread-streams` changed, then calls `ci.Reload`.

State and persistence behavior: raw flag package globals persist process-wide after parsing. Applying config path changes global config storage path; temp dir writes environment variables; cache dir updates config package global cache path. `ci` is mutated in place.

Dependencies and integration points: depends on pflag, config path helpers, rclone header parsers, metadata, network DNS lookup, and global `ConfigInfo.Reload`. It is part of CLI startup.

Risks: conflict errors call `fs.Fatalf`, exiting the process. `net.LookupIP` for `--bind` may depend on DNS and must return exactly one address. Package-level raw values make repeated flag parsing in tests difficult unless reset. DSCP names must remain accurate.

Test signals: no direct tests in this subset for configflags; behavior is indirectly validated by CLI/config tests elsewhere.
