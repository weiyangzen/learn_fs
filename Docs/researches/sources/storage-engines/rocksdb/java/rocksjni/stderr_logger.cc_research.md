<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/stderr_logger.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/stderr_logger.cc

Purpose: Bridges Java `org.rocksdb.util.StdErrLogger` to C++ `ROCKSDB_NAMESPACE::StderrLogger`.

Important APIs/types/functions: `newStdErrLogger` constructs a shared `StderrLogger` with an `InfoLogLevel` and optional prefix string. `setInfoLogLevel`, `infoLogLevel`, and `disposeInternal` mutate/read/delete the shared pointer wrapper.

Control flow: Constructor casts the Java log-level byte to `InfoLogLevel`; if a prefix exists, it copies it with `JniUtil::copyStdString`. Later methods dereference the shared pointer and call logger accessors.

State and persistence behavior: The logger writes to stderr when used by RocksDB. This file stores only the native logger object and its level/prefix.

Dependencies and integration points: Includes `util/stderr_logger.h`, generated `org_rocksdb_util_StdErrLogger.h`, conversion helpers, and `portal.h`. The shared logger handle can be passed into options and SST file manager construction.

Risks: Log-level byte is cast directly with no validation. Prefix copy failure returns 0 with a pending exception. Handle misuse can crash. The logger's stderr side effects can affect tests that assert clean output.

Test signals: Tests should verify prefix/no-prefix construction, log-level get/set, integration with options or SstFileManager, and clean disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/stderr_logger.cc -->
