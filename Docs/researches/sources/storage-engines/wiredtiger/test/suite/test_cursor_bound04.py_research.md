## sources/storage-engines/wiredtiger/test/suite/test_cursor_bound04.py

### Purpose
`test_cursor_bound04.py` covers special bounded traversal scenarios, especially switching between `next()` and `prev()` and manipulating bounds on positioned cursors. It validates cursor behavior when bounds are cleared while positioned and when callers attempt to reset bounds after movement.

### Important APIs, Types, and Functions
The class uses `bound_base`, `make_scenarios`, `create_session_and_cursor`, `set_bounds`, `cursor.next`, `cursor.prev`, `cursor.get_key`, `cursor.set_key`, `cursor.bound`, `cursor_traversal_bound`, and `assertRaisesWithMessage`.

### Control Flow and State
`test_bound_special_scenario` sets lower or upper bounds, advances the cursor, and verifies first returned keys. It then tries to set new bounds with a positioned cursor and explicitly set keys, expecting invalid-argument errors. It also checks inclusive bound changes on positioned cursors, clearing bounds on positioned cursors, and continuing traversal outside the old range after clearing. `test_bound_combination_scenario` validates alternating `next`/`prev`: walking forward from a lower bound then stepping backward to the bound, walking backward from an upper bound then stepping forward, traversing an entire bounded range then reversing direction, and clearing bounds before traversing in the opposite direction.

### Persistence and Integration
The test relies on populated keys from `bound_base`, with optional eviction. It applies the same operations to file, table, and column-group scenarios with simple and composite keys.

### Risks and Test Signals
The major risks are stale cursor position interacting incorrectly with new bounds, direction-change logic crossing bounds, and clear operations leaving internal low/high cursors partially constrained. Passing indicates bounded cursors remain coherent across bidirectional movement.
