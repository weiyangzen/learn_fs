# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/HistogramData.java

Purpose: immutable Java data holder for histogram statistics: median, P95, P99, average, standard deviation, max, count, sum, and min.

Control flow is constructor-only assignment plus simple getters. The older constructor fills max/count/sum/min with zero defaults, preserving compatibility. State is copied Java metrics data, likely created by `Statistics` JNI calls. Dependencies include statistics/histogram APIs but no native handle.

Risks: no equality/toString helpers, sum is `long` while other distribution fields are `double`, and the compatibility constructor can hide absent min/max/count fields as zero. Tests should verify constructor field order, values from `Statistics.getHistogramData`, and behavior for empty histograms.
