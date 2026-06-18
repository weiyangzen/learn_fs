# sources/storage-engines/wiredtiger/test/cppsuite/src/component/statistics/cache_limit.cpp

Purpose: Implements a statistic checker for cache usage as a percentage of configured maximum cache bytes.

Important APIs/types/functions: constructor delegates to `statistics` with no single WT stat field. `get_value` reads image bytes, other bytes, and max bytes from the connection statistics cursor and returns `(image+other)*100/max`. `check` fails if use percentage exceeds configured `max`.

Control flow: called by metrics monitor during runtime or finish depending on config.

State and persistence: no state beyond inherited min/max/name flags; reads live statistics only.

Dependencies/integration: uses `metrics_monitor::get_stat`, WiredTiger stat ids, logger, and `test_util`.

Risks and test signals: asserts max cache bytes is positive and multiplication stays within `INT64_MAX`. A high cache percentage fails immediately with a detailed fatal message.
