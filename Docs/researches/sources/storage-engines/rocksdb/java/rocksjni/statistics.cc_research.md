<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/statistics.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/statistics.cc

Purpose: Bridges Java `Statistics` to a JNI-specific `StatisticsJni` subclass of RocksDB `StatisticsImpl`.

Important APIs/types/functions: Overloaded `newStatistics` constructors optionally clone/wrap another statistics shared pointer and accept a byte array of histograms to ignore. `disposeInternalJni` deletes the shared pointer wrapper. Accessors expose stats level, ticker counts, get-and-reset ticker counts, histogram data/string, reset, and `ToString`.

Control flow: Constructor paths funnel into `newStatistics___3BJ`, convert Java histogram enum bytes to C++ `Histograms`, copy an optional existing shared pointer, allocate `std::shared_ptr<StatisticsJni>`, and return it. Accessors reinterpret the handle as `std::shared_ptr<Statistics>*` and call virtual methods.

State and persistence behavior: Statistics are in-memory counters and histograms. Reset mutates them. Persistence is indirect only through observability/logging outside this file.

Dependencies and integration points: Depends on `rocksdb/statistics.h`, generated `org_rocksdb_Statistics.h`, conversion helpers for ticker/histogram/stats-level enums, `HistogramDataJni`, `RocksDBExceptionJni`, and `statisticsjni.h`.

Risks: Histogram ignore-list naming is inverted at the Java API level if callers expect enabled histograms; the actual subclass disables listed types. Handles are asserted but not runtime-validated. HistogramData construction depends on cached Java class/method lookups. Very large unsigned counters are cast to `jlong`.

Test signals: Tests should verify ignored histograms are disabled, stats level mapping, ticker count and get-and-reset behavior, histogram data object fields, reset error propagation, and cloning/forwarding from another statistics instance.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/statistics.cc -->
