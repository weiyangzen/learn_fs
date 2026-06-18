# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/LoggerTest.java

## Purpose

Tests Java custom logger callbacks, log-level filtering, `Options` and `DBOptions` logger attachment, and runtime log-level changes.

## Important APIs, control flow, and dependencies

Each test creates an anonymous `Logger` overriding `log(InfoLogLevel, String)` and counting messages. It attaches the logger to `Options` or `DBOptions`, opens a DB, and asserts message counts under `DEBUG`, `WARN`, or `FATAL`. Runtime tests change `logger.setInfoLogLevel` after opening, then write and flush to cause messages.

## State, persistence, risks, and test signals

Temporary DB opens trigger native log messages. The state under test is Java callback lifetime, logger log-level state, and option ownership. Risks include callbacks after logger close, missing callback filtering, and DBOptions/Options divergence. Signals are message count greater than zero at debug, zero at warn/fatal for open paths, getter equality for log levels, and nonzero messages after runtime switch to debug.
