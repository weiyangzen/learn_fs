# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/StdErrLoggerTest.java

Purpose: Smoke tests that a native `StdErrLogger` can be constructed and attached to Java `Options` and `DBOptions`.

Important APIs/types/functions: `StdErrLogger(InfoLogLevel, prefix)`, `Options.setLogger`, `DBOptions.setLogger`.

Control flow and state: each test creates options plus a stderr logger in try-with-resources and sets the logger on the options object. It deliberately avoids emitting logs to keep test output clean.

State and persistence behavior: native logger/options state only; no database is opened and no log is persisted.

Dependencies and integration points: RocksJava native library, logger JNI, `InfoLogLevel`.

Risks: does not verify actual stderr output, prefixes, log-level filtering, or lifetime interaction with an open DB. It only catches construction and setter failures.

Test signals: smoke signal for logger object creation and option attachment.
