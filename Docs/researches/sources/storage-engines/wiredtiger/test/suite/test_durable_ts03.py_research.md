# sources/storage-engines/wiredtiger/test/suite/test_durable_ts03.py

Purpose: checks that checkpoints honor durable timestamps and that recovery exposes only updates durable at the relevant stable timestamp.

Important APIs and control flow: scenarios cover integer row-store and column-store byte values. The test loads 3000 rows with value A at timestamp 50, advances stable/oldest to 100 and checkpoints, then prepares per-row updates to value B with commit 200 and durable 220. It reads the checkpoint cursor and read timestamp 150 as A, reads timestamps 210 and 220 as B, checkpoints with `use_timestamp=true`, reopens with stable/oldest 210 and expects A, then writes value C with durable 240, advances stable to 250, checkpoints, reopens, and expects C.

State and persistence: state spans checkpoint snapshots, timestamped prepared updates, restart recovery, and a small 10 MB cache. The test distinguishes visible-but-not-yet-durable value B from value C that is durable before the final stable timestamp.

Dependencies and integration: uses `wttest`, `make_scenarios`, timestamp APIs, checkpoints, and storage engine eviction/history interactions.

Risks and test signals: tiered is skipped due to hook crashes. Failures indicate checkpoints or recovery included updates whose durable timestamp was too new, or failed to preserve updates whose durable timestamp was stable.
