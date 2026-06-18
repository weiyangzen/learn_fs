<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_follower05.py

Purpose: verifies a follower picks up and applies file ID high-water marks so new tables created after step-up do not reuse old leader file IDs.

Important APIs/types/functions: uses `metadata_helper.extract_id`, `metadata:` cursors, `disagg_advance_checkpoint`, role reconfiguration, `debug=(skip_checkpoint=true)` close, and layered table creation/drop.

Control flow: the leader creates 100 layered tables and checkpoints, then scans metadata entries to record the maximum file ID. It drops those tables and checkpoints again. A follower opens, advances to the latest checkpoint, the original leader is closed without a shutdown checkpoint, and the follower steps up. The new leader creates another table, checkpoints, scans metadata again, and asserts the new maximum file ID is greater than the old leader high-water mark.

State and persistence behavior: checkpoint metadata must carry enough ID allocation state for a promoted follower to allocate monotonically increasing IDs even after old objects were dropped.

Dependencies/integration points: integrates metadata parsing, disaggregated checkpoint pickup, PALite/double-free avoidance by skip checkpoint, and file ID allocation. Risks are metadata format changes affecting `extract_id`. Test signal is `follower_max_file_id > max_file_id`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower05.py -->
