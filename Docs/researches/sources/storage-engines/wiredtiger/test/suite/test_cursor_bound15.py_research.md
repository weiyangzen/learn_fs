## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound15.py

### Purpose
`test_cursor_bound15.py` checks `search_near` exact/direction return values with explicit bounds and prefix bounds. It targets edge cases where the nearest visible key lies at, inside, or just outside the configured range.

### Important APIs, Types, and Functions
The class inherits from `bound_base`, uses `set_prefix_bound`, and runs string and byte-array formats with eviction/no-eviction. It uses timestamped inserts, `cursor.search_near`, `cursor.get_key`, `cursor.reset`, and `set_bounds`.

### Control Flow and State
The test inserts `aaa` through `aay` at timestamp 200 and `aaz` at timestamp 50, optionally evicts, then reads at timestamp 250. Lower-only cases search keys beyond the upper end and expect nearest previous/next results with exact values `-1`, `0`, or `1`. Upper-only and both-bound cases similarly validate returned key and direction. Prefix-bound cases use prefixes `aaz`, `aaa`, and `a`, including searches such as `aaza`, `ab`, `aac`, and `aa`, to ensure return values match the closest visible key within prefix-derived bounds.

### Persistence and Integration
Timestamped data and optional eviction exercise search-near logic over both update chains and disk pages. Byte-array normalization is handled by `check_key`.

### Risks and Test Signals
The risk is not just wrong key selection but wrong `search_near` sign, which callers use to know whether the returned key is before or after the search key. Passing confirms exactness semantics survive bound and prefix-bound repositioning.
