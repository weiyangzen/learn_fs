# sources/test-tools/syzkaller/pkg/stat/sample/pvalue.go

## Purpose

`pvalue.go` exposes a Mann-Whitney U test for two `Sample` values by reusing benchmark-statistics code.

## Important APIs, Types, And Control Flow

`UTest(old, new *Sample) (float64, error)` wraps each sample's `Xs` slice in `benchstat.Metrics{RValues: ...}` and calls `benchstat.UTest`. It returns the p-value and any error from benchstat.

## State, Dependencies, Integration, Risks, And Test Signals

The function is stateless and does not sort or copy sample data. It depends on `golang.org/x/perf/benchstat`, with a comment noting the internal stats package is inaccessible. Integration is statistical comparison of experiment/benchmark samples. Risks are upstream API drift, sample-size validation errors, and callers assuming a direction/effect size that p-value alone does not provide. There are no direct tests here; `sample_test.go` covers only percentile/outlier helpers.
