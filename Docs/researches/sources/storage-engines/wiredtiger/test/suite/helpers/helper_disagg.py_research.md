# sources/storage-engines/wiredtiger/test/suite/helpers/helper_disagg.py

Purpose: helper library for disaggregated-storage Python tests. It provides scenario generation, connection/extension config, leader/follower checkpoint manipulation, oplog-style workload generation/checking, and palite page-log corruption utilities.

Important APIs and control flow: top-level helpers generate disaggregated scenarios from test variables, ignore expected RTS output, and compute palite shard IDs. `disagg_test_class` decorates test classes to mix in `DisaggConfigMixin`, create follower/kv_home directories, load page-log extensions, and add `disaggregated=(page_log=...)` config. `DisaggConfigMixin` builds configs, loads extensions, gets complete checkpoint metadata, advances follower checkpoints, switches leader/follower roles, reopens/restarts without local files, and saves old files. `Oplog` generates timestamped inserts/updates/removes, applies them to sessions, and checks point reads plus scans. `DisaggCorruptionMixin` uses built `sqlite3` to inspect/mutate palite `pages_NN.db` rows.

State and persistence behavior: creates `follower`, `kv_home`, `SAVE.N` directories, symlinks, page-log SQLite files, and WiredTiger data files. It mutates connection roles and checkpoint metadata. Corruption helpers directly update/delete palite page rows while the WT connection is closed.

Dependencies and integration points: depends on `wttest`, `wiredtiger`, `run.wt_builddir`, page-log extension APIs (`get_page_log`, `pl_get_complete_checkpoint`), subprocess `sqlite3`, and palite schema/flag constants.

Risks: tightly coupled to palite internals, SQLite file layout, shard count 17, and `WT_PAGE_LOG_DISCARDED`. Role switching and corruption require careful open/closed connection ordering. Decorator-generated classes preserve names but can obscure MRO and setup behavior.

Test signals: follower checkpoint advancement, leader/follower switch tests, oplog consistency checks at timestamps, and expected failures after injected corruption validate this helper.
