## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound_fuzz.py

### Purpose
`test_cursor_bound_fuzz.py` is a randomized correctness fuzzer for cursor bounds. It generates random bounds, random updates/removes/truncates, optional prepared transactions, and random cursor operations, then validates WiredTiger cursor results against an in-memory model.

### Important APIs, Types, and Functions
The file defines enums `operations`, `key_states`, `bound_scenarios`, and `bound_type`, plus a `key` model class. The test uses `wtbound.bound` and `wtbound.bounds`, `WiredTigerTestCase`, `make_scenarios`, random value generation, timestamped transactions, `session.truncate`, `cursor.next`, `prev`, `search`, `search_near`, `WT_NOTFOUND`, and `WT_PREPARE_CONFLICT`.

### Control Flow and State
The fuzzer initializes a key range of 1,000 keys in normal runs or 10,000 in long tests, pre-generates values, and mirrors every database operation into `self.key_range`. For each iteration it applies random lower/upper bounds, performs either batch updates/removes or a truncate, sometimes inside a prepared transaction, then starts a read transaction at the current timestamp and runs one random bound scenario. `run_next` and `run_prev` validate every visible key and every skipped deleted/out-of-bound key. `run_search` validates exact lookups, including prepare conflicts. `run_search_near` checks returned keys are visible, in-bounds, and closest according to deletion and bound state. Prepared conflicts are accepted only when the model contains a prepared key along the path/range.

### Persistence and Integration
The test uses file/table scenarios and row/column key formats. Timestamp commits, checkpoints every ten iterations, prepared commits, and optional truncates exercise multiple storage paths while keeping an authoritative in-memory model.

### Risks and Test Signals
Risks include rare combinations not covered by deterministic tests: deleted gaps, prepared conflicts after internal skips, search-near outside bounds, non-inclusive endpoints, and truncate side effects. The seed is printed for reproduction. Passing gives high confidence in global bounded cursor invariants under randomized mutation.
