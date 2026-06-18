<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/statisticsjni.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/statisticsjni.cc

Purpose: Implements `StatisticsJni`, a `StatisticsImpl` subclass that can disable selected histogram types for Java-created statistics objects.

Important APIs/types/functions: Constructors forward an optional underlying `std::shared_ptr<Statistics>` to `StatisticsImpl` and store `m_ignore_histograms`. `HistEnabledForType` returns false for out-of-range types and for any type in the ignore set.

Control flow: Statistics recording calls the virtual `HistEnabledForType`; this override gates histogram collection based on `HISTOGRAM_ENUM_MAX` and the ignore set.

State and persistence behavior: The only local state is the immutable set of ignored histogram IDs. It affects in-memory metrics collection only.

Dependencies and integration points: Includes `rocksjni/statisticsjni.h`, which depends on RocksDB monitoring internals. Constructed by `statistics.cc`.

Risks: The constructor takes the ignore set by value and stores a copy, which is safe but maybe unnecessarily copies. Type IDs are `uint32_t`; enum conversion correctness depends on `HistogramTypeJni`.

Test signals: Unit tests should call through Java statistics constructors with ignored histogram IDs and verify `getHistogramData` remains empty/unchanged while non-ignored histograms collect data.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/statisticsjni.cc -->
