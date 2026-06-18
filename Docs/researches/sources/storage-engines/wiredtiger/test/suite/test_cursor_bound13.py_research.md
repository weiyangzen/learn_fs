## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound13.py

### Purpose
`test_cursor_bound13.py` validates prefix-bounded `search_near` when matching keys span multiple pages. It protects against early exit before reaching a visible key on another page.

### Important APIs, Types, and Functions
The class uses `WiredTigerTestCase`, `make_scenarios`, and `set_prefix_bound`. It runs variable string and byte-array key formats. The test uses large repeated string keys (`key_size=200`) and `debug=(release_evict=true)` to force multi-page/on-disk behavior.

### Control Flow and State
The test inserts large keys based on `aaa` through `aay` at timestamp 200 and `aaz` at timestamp 50, then evicts them. At read timestamp 100, only the large `aaz` key is visible. Unbounded `search_near` from several locations returns that key. Prefix-bound cases for `a`, `aa`, `aaz`, and the full repeated key must also find the visible `aaz` key, even though traversal may cross page boundaries.

### Persistence and Integration
Timestamped visibility plus forced eviction creates a page layout where prefix-bound search optimization must cooperate with row-search traversal. Byte-array scenarios ensure binary key comparisons follow the same logic.

### Risks and Test Signals
The regression risk is that bounded search-near exits at a page boundary or synthetic upper bound before seeing the only visible key. Passing confirms multi-page prefix searches remain correct after migration to cursor-bound logic.
