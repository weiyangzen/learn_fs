# sources/storage-engines/wiredtiger/test/cppsuite/src/component/statistics/cache_limit.h

Purpose: Declares the cache-limit statistic specialization.

Important APIs/types/functions: `cache_limit` inherits `statistics`, overrides `check` and `get_value`, and is constructed from config plus stat name.

Control flow: metrics monitor treats it through the base `statistics` interface.

State and persistence: inherited configuration state only; no persisted data.

Dependencies/integration: includes configuration, scoped cursor, and base statistics.

Risks and test signals: callers should configure sensible max bounds because this checker ignores base `field` and computes a derived percentage.
