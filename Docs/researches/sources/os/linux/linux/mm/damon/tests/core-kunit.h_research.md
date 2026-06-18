# File Research: sources/os/linux/linux/mm/damon/tests/core-kunit.h

KUnit tests for the DAMON core. The header is included by the core implementation under `CONFIG_DAMON_KUNIT_TEST`, giving tests access to static helpers and internal data structures.

Coverage areas:
- Region and target lifecycle: allocation, insertion, counting, destruction, and list traversal.
- Aggregation reset: `kdamond_reset_aggregated()` clears per-region access counters while preserving targets and regions.
- Region splitting and merging: `damon_split_region_at()`, `damon_merge_two_regions()`, `damon_merge_regions_of()`, and `damon_split_regions_of()`.
- Operations registration: valid registration, duplicate registration rejection, unregister/re-register behavior, and invalid ops selection.
- Explicit region setting: `damon_set_regions()` trims, creates, and preserves regions according to configured ranges.
- Access-rate conversions and monitoring result updates across changed sample/aggregation intervals.
- Attribute validation in `damon_set_attrs()`.
- Moving-sum helper behavior.
- DAMOS filter allocation and commit semantics.
- Quota goal, quota, and migration destination commit semantics.
- DAMOS scheme commit behavior for pageout and migrate-hot examples.
- Target-region commit behavior and `damon_commit_ctx()` validation.
- Address-range filter splitting behavior in `damos_filter_match()`.
- Feedback-loop next-input behavior.
- Default-reject calculation for mixed core and ops filters.
- Minimum region count enforcement via `damon_apply_min_nr_regions()`.
- `damon_is_last_region()` correctness while appending regions.

Important invariants captured by tests:
- Merging adjacent regions uses size-weighted access count and age calculations.
- Splitting a region preserves access-rate, last-access, and age metadata in both halves.
- `damon_set_attrs()` rejects too-low minimum region count, `max < min`, and aggregation intervals shorter than the sample interval.
- `damon_commit_ctx()` rejects non-power-of-two `min_region_sz`.
- `damos_commit_quota_goal()` preserves PSI `last_psi_total` when committing a PSI goal onto an existing PSI goal.
- `damos_commit_quota_goals()` resizes destination goal lists to match the source list.
- `damos_commit_dests()` handles same-size, growth, shrink, empty-to-nonempty, and nonempty-to-empty destination arrays.
- `damos_commit_filter()` copies type-specific fields for memcg, address, target, and hugepage-size filters.
- Address filters can split a region at filter boundaries so matching and nonmatching subranges are separated.
- Core and ops filters affect `core_filters_default_reject` and `ops_filters_default_reject` differently depending on whether the last filter is an allow or reject filter and which layer handles it.

Structure:
- Individual `static void` test functions are registered in `damon_test_cases`.
- The suite name is `damon`.
- Tests skip with `kunit_skip()` on allocation failure or impossible architecture-specific setup.

Relationship to production code:
- This file does not provide production functionality, but it codifies assumptions that `core.c`, `sysfs-schemes.c`, and backend ops depend on.
- It is especially useful as executable documentation for DAMOS commit semantics, region mutation rules, and filtering behavior.
