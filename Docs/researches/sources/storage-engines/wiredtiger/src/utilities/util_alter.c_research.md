## sources/storage-engines/wiredtiger/src/utilities/util_alter.c

Purpose: implements `wt alter`, a thin CLI wrapper over `WT_SESSION.alter` for applying configuration changes to one or more URIs.

Important APIs/types/functions: `util_alter` parses only `-?`, validates that remaining arguments are URI/configuration pairs, and calls `session->alter(session, configp[0], configp[1])` for each pair. The static `usage` function documents `alter uri configuration ...`.

Control flow: after option parsing, argument count must be nonzero and even. The function walks the remaining argv two entries at a time. On the first `session->alter` failure it reports `session.alter: uri, config` with `util_err` and returns `1`; otherwise it returns `0`.

State and persistence behavior: alters metadata and object configuration through the WiredTiger session API. Whether changes are persisted, rejected, or require clean trees is enforced by the library. This wrapper does no URI defaulting; callers must pass the intended URI string.

Dependencies and integration points: dispatched from `util_main.c` under an already opened connection/session. Uses `__wt_getopt` global state and `util_usage`/`util_err`. It depends on WiredTiger session alter semantics for validation and locking.

Risks: it accepts arbitrary URI strings and config pairs without `util_uri` normalization, so shorthand table names are not expanded here. Partial success is possible: earlier pairs may have altered objects before a later pair fails. There is no transaction-like grouping of multiple alterations.

Test signals: usage tests for odd/missing arguments, successful alter of table configuration, error propagation for invalid config/URI, and multi-pair behavior where the loop stops on the first failure.
