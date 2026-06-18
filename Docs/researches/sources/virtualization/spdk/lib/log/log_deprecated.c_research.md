# File Research: sources/virtualization/spdk/lib/log/log_deprecated.c

Implements SPDK's deprecation registry and rate-limited warning emission for deprecated features.

Key entry points:
- `spdk_log_deprecation_register()` creates a deprecation record with tag, description, target removal release, and warning rate limit.
- `spdk_log_deprecated()` records a hit and emits a warning when not suppressed by rate limiting.
- `spdk_log_deprecation_find_by_tag()` looks up a registered deprecation.
- `spdk_log_for_each_deprecation()` iterates all registered deprecations.
- `spdk_deprecation_get_tag()`, `spdk_deprecation_get_description()`, `spdk_deprecation_get_remove_release()`, and `spdk_deprecation_get_hits()` expose deprecation metadata.

Core mechanics:
- A constructor records a monotonic epoch at library load time.
- Timestamps are tracked as nanoseconds since that epoch using `CLOCK_MONOTONIC`.
- Each deprecation record stores hit count, last logged time, rate-limit interval, and deferred warning count.
- Rate-limited calls increment `deferred` and return without logging until the interval expires.
- When a warning is emitted after suppression, an additional warning reports how many messages were suppressed.

Important invariants:
- Tags, descriptions, and removal-release strings must fit in fixed-size arrays; this is enforced with assertions before allocation.
- A null deprecation pointer is treated as a programmer error: it logs, asserts false, and returns.
- The implementation intentionally accepts approximate counters under multithreaded races to avoid locking hot paths.

Filesystem/block relevance:
- Storage APIs evolve over time; this file provides a uniform way for block and filesystem-adjacent SPDK modules to flag deprecated behavior while limiting log volume.

Notable risks:
- The global `g_deprecations` list is not protected by a lock.
- Hit, deferred, and last-log updates are racy by design, so statistics are advisory rather than exact.
