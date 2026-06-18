<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/logger.go -->
# sources/storage-engines/badger/logger.go

## Purpose
This file defines Badger's pluggable logging abstraction and default stderr logger. It lets each `Options` value carry its own logger and logging threshold.

## Important APIs, Types, And Functions
`Logger` requires `Errorf`, `Warningf`, `Infof`, and `Debugf`. Methods on `*Options` forward those calls when `Options.Logger` is non-nil and silently drop messages otherwise. `loggingLevel` defines `DEBUG`, `INFO`, `WARNING`, and `ERROR`. `defaultLog` wraps `log.Logger`, and `defaultLogger` creates a logger named `badger ` writing to stderr.

## Control Flow
Callers use `opt.Errorf` and related methods throughout the DB. These methods check `opt.Logger` and delegate. The default logger methods compare the configured level against the message severity before printing with a severity prefix.

## State And Persistence Behavior
The file has no persistent state. The only mutable state is the logger implementation stored in `Options`, plus the standard logger output destination. Logging itself is side-effecting but not part of Badger durability.

## Dependencies And Integration Points
It depends only on Go's `log` and `os` packages. It is used across manifest replay, compaction, memtable recovery, subscription, and value-log code for diagnostics and error reporting.

## Risks And Edge Cases
Nil loggers intentionally suppress all logging, which can make operational diagnosis harder. The default level comparison relies on the enum order: lower numeric values are more verbose. The `Options` receiver is a pointer for log methods, so callers need an addressable options value.

## Test Signals
`logger_test.go` checks forwarding into a mock logger for error/info/warning paths. Debug forwarding and default logger level filtering are not directly tested in the listed tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/logger.go -->
