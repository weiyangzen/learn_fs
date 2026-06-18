# sources/storage-engines/wiredtiger/test/suite/test_disagg_checkpoint_size06.py

Purpose: tests checkpoint-size accounting for disaggregated delta chains, especially WT-16864 scenarios where full-image replacement should obsolete prior delta cumulative sizes.

Important APIs and control flow: helpers read checkpoint size from stable metadata, insert rows, evict a page with `debug=(release_evict)`, and read dsrc/connection stats. Tests build baseline pages, create deltas with `delta_pct=90`, evict to force page-service readback, reconfigure `delta_pct=1` to force full images, checkpoint, and compare size bounds across cycles.

State and persistence: the target state is page-log full images and deltas plus metadata `size=`. Eviction and reconfiguration intentionally move through delta-chain termination paths.

Dependencies and integration: uses `DisaggConfigMixin`, `@disagg_test_class`, page delta config, `wiredtiger.stat`, metadata cursors, and debug eviction.

Risks and test signals: checkpoint size must drop or stabilize after full-image replacement rather than accumulate old deltas. Failures indicate cumulative-size double counting or error-path leaks.
