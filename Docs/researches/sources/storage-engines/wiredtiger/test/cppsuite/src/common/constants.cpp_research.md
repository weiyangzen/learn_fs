# sources/storage-engines/wiredtiger/test/cppsuite/src/common/constants.cpp

Purpose: Defines shared string constants for cppsuite component names, configuration keys, WiredTiger timestamp/config keys, and internal tracking table names.

Important APIs/types/functions: exports names such as `METRICS_MONITOR`, `OPERATION_TRACKER`, `TIMESTAMP_MANAGER`, config keys like `CACHE_SIZE_MB`, `OP_RATE`, `TRACKING_KEY_FORMAT`, timestamp keys like `commit_timestamp`, and table names `table:operation_tracking` and `table:schema_tracking`.

Control flow: no runtime logic; constants are initialized as static storage.

State and persistence: constants influence runtime configuration parsing and persistent table names but hold no mutable state.

Dependencies/integration: matches declarations in `constants.h` and is used throughout components, database setup, operation tracking, and metrics.

Risks and test signals: key-name drift breaks config parsing at runtime. Compile/link failures catch missing declarations; config tests catch semantic mismatches.
