# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/ContinuousSample.java

Purpose: small reservoir sampler for benchmark latency summaries. It retains up to `sampleSize` comparable numeric samples while tracking population size, min, max, mean, median, and percentiles.

Important APIs and flow: `addSample` updates min/max, appends initial samples, then probabilistically replaces a random retained slot with probability `sampleSize / populationSize`. `percentile` lazily sorts retained samples and indexes by floor of percentile position. `toString` reports mean, median, 90th, and 98th percentile.

State and persistence: all state is in memory: `samples`, `populationSize`, `sorted`, and min/max. It has no FoundationDB dependency and is used by `ParallelRandomScan`. Risks include non-thread-safe internal mutation, approximate percentile accuracy, and a subtle reservoir issue where `samples.add(randomIndex, sample)` inserts instead of replacing after capacity. Callers synchronize externally when sharing it.
