# sources/test-tools/syzkaller/pkg/stat/sample/sample.go

## Purpose

`sample.go` provides basic statistical operations over a collection of float64 measurements.

## Important APIs, Types, And Control Flow

`Sample` holds `Xs []float64` and a `Sorted` flag. `Percentile` sorts in place if needed and uses the R8 percentile estimator copied from `x/perf/internal/stats`. `Median` calls `Percentile(0.5)`. `RemoveOutliers` uses Tukey fences based on Q1 and Q3, returning a copied sample unchanged for fewer than four points. `Copy` clones the slice and flag, and `Sort` sorts in place once.

## State, Dependencies, Integration, Risks, And Test Signals

Operations mutate `Sample.Xs` order and `Sorted`, except `Copy` and returned outlier samples. Dependencies are `math` and `slices`. Risks include panics on empty samples, in-place sorting surprises, preserving `Sorted` in the outlier result even though filtered order follows sorted input, and floating-point tolerance. `sample_test.go` covers median ranges and sanity outlier removal.
