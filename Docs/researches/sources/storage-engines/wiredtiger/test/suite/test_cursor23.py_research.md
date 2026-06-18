## sources/storage-engines/wiredtiger/test/suite/test_cursor23.py

### Purpose
`test_cursor23.py` extends raw key/value cursor coverage to dataset-created file and table objects. Its active scenarios exercise simple string key/value formats; the conditional complex-schema path documents the expected unsupported behavior for raw key/value access on complex values.

### Important APIs, Types, and Functions
`test_cursor23` derives from `wttest.WiredTigerTestCase` and uses `SimpleDataSet`, `make_scenarios`, `wiredtiger.WiredTigerError`, `assertRaisesWithMessage`, `cursor.get_raw_key_value`, `cursor.get_key`, and `cursor.get_value`. Scenario fields include `type`, `keyfmt`, `valfmt`, `dataset`, and `complex`.

### Control Flow and State
For each active scenario (`file:` and `table:` with `S/S` formats), the test creates a `SimpleDataSet` with 100 records and opens a cursor. It performs one transaction scanning the first nine rows with `get_key`/`get_value`, then another scanning the same range with `get_raw_key_value`. Expected keys are zero-padded strings such as `000000000000001`, and values follow the `SimpleDataSet` string pattern. The unused `complex=True` branch would validate that complex schema values decode through normal accessors but reject raw key/value access with an operation-not-supported error.

### Persistence and Integration
The dataset helper owns population and naming. The test is integrated with WiredTiger scenario expansion and validates both file and table object cursors through the same accessor path. Transactions are read-only around scans, so persistent state comes from the populated dataset.

### Risks and Test Signals
The test guards against raw accessor regressions for dataset-generated records and against accidental support claims for complex schema tuples. A passing simple scenario confirms that raw tuple retrieval remains compatible with file and table cursors using simple packed formats.
