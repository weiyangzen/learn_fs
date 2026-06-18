# sources/storage-engines/wiredtiger/test/cppsuite/src/main/configuration.h

Purpose: Declares cppsuite's typed configuration wrapper and utility string splitter.

Important APIs/types/functions: `split_string` splits non-empty tokens on a delimiter. `configuration` exposes typed getters for bool, int, string, list, and subconfig values, optional getter variants, and `get_throttle_ms`.

Control flow: callers request required config values and receive fatal errors for missing/mistyped keys; optional methods return defaults or null/empty values.

State and persistence: stores merged configuration and WT parser pointer.

Dependencies/integration: includes `wiredtiger.h` and is consumed by all component and main harness code.

Risks and test signals: returned subconfigs are heap allocated and ownership is transferred to callers/components. List parsing is simple comma splitting after bracket removal and does not handle escaped commas.
