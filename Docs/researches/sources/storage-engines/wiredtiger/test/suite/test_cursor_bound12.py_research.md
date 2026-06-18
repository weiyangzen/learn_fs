## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound12.py

### Purpose
`test_cursor_bound12.py` checks `search_near` return keys under visibility rules and prefix bounds. It compares unbounded nearest-key behavior with bounded prefix behavior at different read timestamps.

### Important APIs, Types, and Functions
The test uses `wttest.WiredTigerTestCase`, `make_scenarios`, and `set_prefix_bound`. Key formats include fixed string `10s`, variable string `S`, and byte array `u`; eviction is optional. `check_key` normalizes expected keys for byte and fixed-length string formats.

### Control Flow and State
The test inserts `aaa` through `aay` at timestamp 200, `aaz` at timestamp 50, and `aazab` at timestamp 250, optionally evicting all keys. At read timestamp 100, only `aaz` is visible; unbounded searches from nearby prefixes return it, while prefix bounds for `az` or `b` return `WT_NOTFOUND`. At timestamp 25 no keys are visible. At timestamp 250 all keys are visible; unbounded and prefix-bounded searches return the nearest matching key for prefixes such as `a`, `aa`, `aaz`, and `aaza`, while prefix `az` has no match.

### Persistence and Integration
Timestamped commits and optional eviction test search-near visibility on both in-memory and reconciled pages. Prefix bounds are implemented by setting inclusive lower and exclusive synthetic upper bounds.

### Risks and Test Signals
The suite catches cases where `search_near` returns a key outside bounds, ignores visibility, or misreports direction/exactness around prefixes. Passing confirms prefix-bounded search-near respects both timestamps and key format normalization.
