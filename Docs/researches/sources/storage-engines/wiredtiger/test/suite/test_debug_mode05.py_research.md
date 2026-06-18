# sources/storage-engines/wiredtiger/test/suite/test_debug_mode05.py

Purpose: exercises table logging debug mode with rollback-to-stable behavior, ensuring logged updates and timestamp rollback coexist.

Important APIs and control flow: with logging and `debug_mode=(table_logging=true)` enabled, the test creates a file, writes timestamped values, advances stable timestamps, checkpoints, writes newer values, calls rollback-to-stable, and verifies the stable version is visible.

State and persistence: state spans the update chain, log records, stable timestamp, and checkpointed table content. The core persistence signal is that rollback-to-stable discards unstable updates without corrupting the logged table.

Dependencies and integration: uses `wttest`, timestamps, transaction commit timestamps, `conn.set_timestamp`, checkpoints, and `conn.rollback_to_stable`.

Risks and test signals: this test is vulnerable to timestamp ordering or logging semantics changes. It is an integration guard for debug table logging paths that otherwise tend to be covered by log byte inspection rather than rollback behavior.
