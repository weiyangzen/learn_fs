# sources/storage-engines/wiredtiger/test/cppsuite/src/bound/bound.cpp

Purpose: Implements a small value object for applying one WiredTiger cursor bound.

Important APIs/types/functions: constructors create an empty bound, explicit key/lower/inclusive bound, or random key bound with optional forced first character. `get_config` formats `bound=lower|upper,inclusive=true|false`; `get_key` and `get_inclusive` expose state; `apply` sets the cursor key and calls `cursor->bound`; `clear` resets to empty/default.

Control flow: random constructors use thread-local `random_generator`; `apply` is immediate and fatal on WT error via `testutil_check`.

State and persistence: holds `_key`, `_inclusive`, and `_lower_bound` in memory only. It changes cursor-bound state but does not persist data.

Dependencies/integration: depends on `bound.h`, `random_generator`, `constants`, `scoped_cursor`, and `test_util`.

Risks and test signals: random-key generation is nondeterministic unless higher-level tests seed behavior elsewhere. Applying an empty/default bound would set an empty key, so callers must construct meaningful bounds. Cursor-bound WT return codes are asserted.
