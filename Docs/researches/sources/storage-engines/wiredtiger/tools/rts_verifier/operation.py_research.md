# sources/storage-engines/wiredtiger/tools/rts_verifier/operation.py

Purpose: parses individual `WT_VERB_RTS` verbose log lines into typed operation objects with fields used by the checker.

Important APIs and control flow: `OpType` enumerates RTS message categories. `Operation.__init__()` extracts the bracketed RTS message name with a regex, lowercases it, dispatches to `__init_<name>()`, and leaves parsed attributes on `self`. Helpers parse file/tiered names, timestamp tuples, and pointer values with platform-specific pointer formats. The many `__init_*` methods parse tree visits, logging state, page rollback, update aborts, page abort checks, history-store updates, checkpoint recovery, stable timestamp state, page delete, update-chain verify, and other RTS messages. `_TIME_WINDOW_REGEX` centralizes parsing of verbose time-window structures.

State and persistence behavior: each `Operation` is immutable by convention after parsing but stored as a regular object with dynamic attributes. It does not write files or external state.

Dependencies and integration points: imported by `rts_verify.py` and `checker.py`. It depends on exact text formats emitted by WiredTiger RTS verbose logging and enums from `basic_types.py`.

Risks: parsing is brittle: most regex matches are used without checking for `None`, so message-format drift crashes verification. Some handlers appear to set incorrect types or fields, such as `__init_hs_update_restored()` setting `OpType.HS_UPDATE_VALID`, `__init_stable_pg_walk_skip()` setting `KEY_REMOVED`, and several copied timestamp assignments using start values for stop fields. `SKIP_DEL = 45,` creates a tuple value in the enum definition. Some boolean parses use `.lower` without calling it. These risks matter more once semantic checking is enabled.

Test signals: no direct tests are present. A robust test suite should feed representative `WT_VERB_RTS` lines for every `OpType`, assert parsed fields, and assert parser failures for malformed lines.
