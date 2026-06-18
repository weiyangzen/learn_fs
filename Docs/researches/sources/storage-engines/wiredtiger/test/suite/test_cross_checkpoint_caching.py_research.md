<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cross_checkpoint_caching.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cross_checkpoint_caching.py

Purpose: tests disaggregated follower cross-checkpoint disk-image caching: unchanged pages should hit cache when scanning a later checkpoint.

Important APIs and control flow: the class is decorated with `disagg_test_class` and scenario-generated disaggregated storage. The leader creates a layered table with tiny page sizes, the follower opens the same object, the leader inserts 5000 rows and checkpoints, the follower advances and scans while measuring shared-disk miss/hit deltas, then the leader updates one row, checkpoints, and the follower scans again. The second scan must have misses for rewritten pages and hits for unchanged pages, with `second_hit == first_miss - second_miss`.

State, persistence, and dependencies: state spans leader/follower homes, disaggregated storage checkpoints, shared disk-image cache stats, and layered table pages. Dependencies are `helper_disagg`, `wiredtiger.stat`, and checkpoint advancement.

Integration points: targets disaggregated storage, follower checkpoint visibility, page-image cache accounting, and layered cursors.

Risks and test signals: page-size choices are tuned to avoid splits and preserve predictable rewritten paths. Failures indicate cache accounting, checkpoint advancement, or disaggregated page identity regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cross_checkpoint_caching.py -->
