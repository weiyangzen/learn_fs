# sources/sync-backup/casync/test/test-cachunker.c

Purpose: unit test for rolling hash and chunk-size configuration behavior.

Important APIs/types/functions: `test_rolling` verifies rolling hash add/remove symmetry over a window, `test_chunk` checks chunk boundaries on random data stay within min/max limits, and `test_set_size` validates size presets/parsing.

Control flow/state: initializes `CaChunker`, reads random buffers, feeds data in chunks, and asserts invariants.

Dependencies/integration: covers `cachunker.h`, util assertions, `/dev/urandom`, and size parsing behavior.

Risks/test signals: random-data chunking may not hit every boundary case but should catch broken rolling hash/window logic quickly.

Source research group: `subset-b-009122`.
