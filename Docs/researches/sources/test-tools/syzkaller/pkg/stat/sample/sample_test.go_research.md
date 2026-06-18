# sources/test-tools/syzkaller/pkg/stat/sample/sample_test.go

## Purpose

This file tests sample median and outlier-removal behavior.

## Important APIs, Types, And Flow

`TestMedian` checks odd and even input sets using min/max tolerance rather than exact floating equality. `TestRemoveOutliers` checks Tukey-fence behavior for a low outlier, a high outlier, and a spread with no outliers, then sorts the result and compares slices.

## State, Dependencies, Risks, And Test Signals

The tests use deterministic `Sample` values and `reflect.DeepEqual`. They do not cover empty input, percentile endpoints, copy behavior, sorted-flag preservation, or U-test p-values. Passing tests indicate the chosen R8 percentile and Tukey-fence implementations behave sanely on representative small samples.
