# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable28.py

Purpose: tests recovery RTS with `debug_mode=(update_restore_evict=true)` and verifies write-generation metadata after update-restore eviction. It currently runs the integer row-store scenario.

Important APIs/types/functions: extends the RTS base; `conn_config` enables statistics/RTS verbosity and `conn_recon` adds low cache and update-restore eviction debug mode. Defines `parse_write_gen` using metadata cursor regexes for `write_gen` and `run_write_gen`. Uses `large_updates`, `session.checkpoint`, `simulate_crash_restart`, and `stat.conn.cache_eviction_force_retune`-style update-restore counters.

Control flow: writes stable values through timestamp 40, sets stable to 40, writes newer values at 50/60/70, checkpoints, parses checkpoint metadata write generations, restarts with update-restore eviction enabled, parses metadata again, reads update-restored page stats, and validates all post-stable reads return the timestamp-40 value.

State and persistence behavior: recovery must rollback checkpointed unstable updates and assign newer run write generations to pages it update-restores. The metadata checks prove recovery generated a new write generation above the prior checkpoint base.

Dependencies and integration points: integrates metadata cursor parsing, debug reconciliation configuration, recovery RTS, and stats for update-restored pages.

Risks: regex strings use `\d` in normal string literals, which triggers Python warnings on newer interpreters. Metadata format changes can break `parse_write_gen`.

Test signals: checkpoint `run_write_gen == 1`, checkpoint write gen greater than run write gen, recovery run write gen greater than old checkpoint write gen, recovery write gen greater than recovery run write gen, positive update-restored pages, and stable-value reads.
