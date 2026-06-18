# sources/storage-engines/wiredtiger/test/suite/test_tiered17.py

## Purpose
`test_tiered17.py` verifies that readonly connection and cursor access do not create new tiered object files.

## Important APIs, Types, and Functions
The class uses `TieredConfigMixin`, `get_conn_config`, `fnmatch`, filesystem object counting, checkpoint cursors, and two shutdown scenarios: clean and unclean. Helpers include `get_object_files`, `verify_checkpoint`, and `populate`.

## Control Flow
`populate` creates and writes a tiered table, checkpoints with `flush_tier`, and optionally writes extra uncheckpointed data for the unclean scenario. `verify_checkpoint` opens the named checkpoint and asserts the object-file count is unchanged. `test_open_readonly_conn` populates, verifies checkpoint open, records object files, reopens the whole connection with `readonly=true`, closes, and asserts no count changes. `test_open_readonly_cursor` reopens normally but opens a readonly cursor and performs the same object-count checks.

## State and Persistence Behavior
The test tracks local `.wtobj` and `.wt` files in the WT home. The invariant is that readonly recovery/open paths must not switch or create tiered objects, even with uncheckpointed data from an unclean-style scenario.

## Dependencies and Integration Points
It integrates with checkpoint cursor open, readonly connection config, readonly cursor config, tiered flush, and filesystem object naming.

## Risks and Test Signals
The risk is accidental object creation during readonly open, checkpoint open, or close. The signal is an unchanged object-file count at each phase.
