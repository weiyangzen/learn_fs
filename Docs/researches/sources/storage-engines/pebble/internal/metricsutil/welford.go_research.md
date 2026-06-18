<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/metricsutil/welford.go -->
# sources/storage-engines/pebble/internal/metricsutil/welford.go

Purpose: provides numerically stable online calculation of mean, sample variance, and standard deviation for unweighted and frequency-weighted samples.

Important APIs/types: `Welford` with `Add`, `Count`, `Mean`, `Variance`, `StdDev`; `WeightedWelford` with `Add(x, frequency)`, `Mean`, `Variance`, and `StdDev`.

Control flow and state: `Welford.Add` updates count, mean, and `m2` using Welford's incremental algorithm. `Variance` returns sample variance `m2/(n-1)` and guards counts below 2. `WeightedWelford.Add` ignores zero frequency, converts frequency to `float64`, tracks total weight, sum of squared weights, mean, and accumulated squared deviation `s`; variance uses `s/(wSum-1)`.

Persistence and integration: all state is in-memory and caller-owned. Dependencies are only `math`. Risks include no synchronization, possible precision loss or overflow for extreme values/frequencies, and `w2Sum` currently being maintained but unused in the reported variance formula. Tests cover basic means and sample variances, including equivalence to repeated samples.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/metricsutil/welford.go -->
