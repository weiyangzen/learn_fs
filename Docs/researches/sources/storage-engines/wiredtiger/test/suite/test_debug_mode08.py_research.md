# sources/storage-engines/wiredtiger/test/suite/test_debug_mode08.py

Purpose: runs inherited base cursor tests with `debug_mode=(cursor_copy=true)` and explicitly tests reconfiguring cursor-copy debug mode off and back on.

Important APIs and control flow: `test_debug_mode08` subclasses `test_base03.test_base03`, so the base suite executes under cursor-copy mode. Its local `test_reconfig` creates a file, opens/writes/closes cursors, reconfigures to `cursor_copy=false`, repeats cursor activity, reconfigures back to the class config, and repeats again.

State and persistence: cursor operations update a file-backed object; persistence is secondary to exercising debug allocation/copy behavior around cursor buffers.

Dependencies and integration: uses `wttest`, `test_base03`, and `conn.reconfigure`.

Risks and test signals: comments note there is no practical way to observe the extra malloc/free behavior directly. The signal is successful execution of broad inherited cursor behavior while the debug flag is enabled.
