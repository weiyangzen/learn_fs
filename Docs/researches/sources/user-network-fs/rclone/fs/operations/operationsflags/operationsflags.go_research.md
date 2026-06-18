# Research: sources/user-network-fs/rclone/fs/operations/operationsflags/operationsflags.go

## sources/user-network-fs/rclone/fs/operations/operationsflags/operationsflags.go

Purpose: defines CLI flag helpers for operations logger/report outputs, kept in a separate package so command wiring can be replaced. APIs include embedded `Help`, `AddLoggerFlagsOptions`, `AnySet`, `AddLoggerFlags`, and `ConfigureLoggers`. `AddLoggerFlags` registers report file flags and related `lsf` formatting flags into a `pflag.FlagSet`, filling `operations.LoggerOpt`.

Control flow in `ConfigureLoggers` normalizes time format, initializes list formatting against the destination filesystem, opens each requested report destination, and returns a closer that logs close failures. State is limited to passed option structs and opened file handles; persistence is the report files created with `os.Create`, or stdout for `-`. Dependencies include Cobra/pflag, rclone flag helpers, hash selection, and `operations.LoggerOpt`. Integration points are sync/check commands that need combined/missing/match/differ/error/dest-after reports. Risks include truncating existing report files, caller responsibility to invoke the closer, and warnings for `--no-traverse` combinations that make some reports incomplete.
