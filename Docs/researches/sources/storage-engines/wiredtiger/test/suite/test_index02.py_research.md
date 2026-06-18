# sources/storage-engines/wiredtiger/test/suite/test_index02.py

Purpose: tests `search_near` behavior on index cursors for exact matches, between-key searches, and empty indexes.

Important APIs and functions: defines a Python `cmp` helper. `test_index02` scenarios include index key `columns=(v)` and index key including primary key `columns=(v,k)`, with `ncol` selecting key width. The test uses table and index cursors, `set_key`, `search_near`, and `get_key`.

Control flow: `test_search_near_exists` populates values and verifies `search_near` on existing index keys returns exact matches. `test_search_near_between` searches for keys not present and validates returned direction/order relative to nearby index entries. `test_search_near_empty` validates behavior on an empty index.

State and persistence behavior: all state is in-memory logical index content created during the test. No persistence or checkpointing is involved.

Dependencies and integration points: integrates index cursor key projection, duplicate/primary-key tie-breaking when index includes table key, and WiredTiger `search_near` return semantics.

Risks and edge cases: correctness depends on key ordering and the number of columns in each index scenario. Empty-index behavior is a separate edge case because no nearest key exists.

Test signals: return values and keys from `search_near` match the expected comparison direction and exact/near key values.
