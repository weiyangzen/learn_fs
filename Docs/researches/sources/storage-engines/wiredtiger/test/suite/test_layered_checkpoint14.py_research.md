# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint14.py

Purpose: ensures follower reads do not access pages that were freed by earlier leader checkpoints in a layered/disaggregated stable file.

Important APIs/types/functions: uses verbose block/read logging, `wiredtiger.stat.conn.disagg_block_page_discard`, filesystem reading of `stdout.txt`, follower `disagg_advance_checkpoint`, and `verifyUntilSuccess`.

Control flow: the leader creates a layered table, inserts 10,000 rows, checkpoints, updates every even key, checkpoints, updates every hundredth key, and checkpoints. It parses `stdout.txt` for `WT_VERB_BLOCK` `block free` lines for the stable file, records freed page IDs, asserts no page freed twice, and checks discard stat increased. It opens a follower with read verbosity, advances checkpoint, scans all rows, then parses read log lines to assert no read page ID was previously freed.

State and persistence behavior: state spans stable file page IDs, freed-page tracking, and follower-visible row count. The test confirms block-free metadata is honored by follower reads after checkpoint pickup.

Dependencies/integration points: verbose logging format, disaggregated block free/discard logic, follower stable reads, statistics, and layered verify.

Risks: strongly coupled to stdout log text and page_id formatting. It also assumes the workload generates frees and follower reads enough stable pages.

Test signals: pass means pages are not double-freed, discard stats move, follower sees all records, and no freed stable page is read.
