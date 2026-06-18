<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/statisticsjni.h -->
# sources/storage-engines/rocksdb/java/rocksjni/statisticsjni.h

Purpose: Declares the JNI-specific `StatisticsJni` class used by Java `Statistics` bindings.

Important APIs/types/functions: `class StatisticsJni : public StatisticsImpl` declares two constructors and overrides `bool HistEnabledForType(uint32_t type) const`. Private member `m_ignore_histograms` stores disabled histogram IDs.

Control flow: The header defines the type contract; construction and histogram filtering implementation live in `statisticsjni.cc`, and allocation lives in `statistics.cc`.

State and persistence behavior: Declares process-local in-memory metric filtering state. No persistence.

Dependencies and integration points: Includes `monitoring/statistics_impl.h` and `rocksdb/statistics.h`, so it uses RocksDB internal statistics implementation rather than only public interfaces. Included by `statistics.cc`.

Risks: Depending on `monitoring/statistics_impl.h` couples the Java binding to RocksDB internal headers. Any change to `StatisticsImpl` virtual methods or constructor signatures can break this bridge.

Test signals: Build compatibility across RocksDB versions is the main signal. Runtime tests should confirm the override is invoked through base `Statistics` handles returned to Java.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/statisticsjni.h -->
