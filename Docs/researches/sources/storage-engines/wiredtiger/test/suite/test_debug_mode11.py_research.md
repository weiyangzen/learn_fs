# sources/storage-engines/wiredtiger/test/suite/test_debug_mode11.py

Purpose: verifies close configuration `debug=(skip_checkpoint=true)` by checking whether uncheckpointed data survives restart.

Important APIs and control flow: scenarios cover normal close and skip-shutdown-checkpoint close. The test creates a table, writes `ckpt_1st`, explicitly checkpoints, writes `ckpt_2nd` without checkpointing, closes with scenario-specific config, reopens, and uses `verify_key` with `WiredTigerCursor` to search for expected values.

State and persistence: `ckpt_1st` is durable because of the explicit checkpoint. `ckpt_2nd` is durable only if shutdown checkpoint runs during close. No logging is enabled to mask the checkpoint behavior.

Dependencies and integration: uses `wiredtiger.WT_NOTFOUND`, `wttest.skip_for_hook("tiered")`, `make_scenarios`, and `helper.WiredTigerCursor`.

Risks and test signals: clear pass/fail signal is visibility after reopen. Tiered storage is skipped because object persistence semantics differ.
