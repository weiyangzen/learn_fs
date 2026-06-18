# sources/storage-engines/wiredtiger/test/format/kv.c

Purpose: defines deterministic key and value generation for format tables, including persisted random key length tables for reopen compatibility and value patterns that support verification, prefix compression, overflow, and RLE testing.

Important APIs and functions: `key_init`, `key_gen_init`, `key_gen_teardown`, `key_gen_common`, `val_init`, `val_gen_init`, `val_gen_teardown`, and `val_gen`; static helpers `key_init_random` and `val_len`.

Control flow: row-store tables get a `key_rand_len` table generated or reloaded from `CONFIG.keylen[.<table id>]`. Key buffers are initialized with alphabetic filler, optional common prefixes are generated from key-number buckets, and keys encode a zero-padded number plus suffix. Values use recognizable base data, zero-length values every 63rd key, duplicate value patterns for variable-column-store RLE, and occasional 80-100 KiB overflow-sized items.

State and persistence: persists key length choices to `g.home_key` so reopened runs regenerate identical row-store keys. It owns `TABLE.val_base`, `TABLE.val_dup_data_len`, and `TABLE.key_rand_len`. Generated data embeds key numbers for readable trace and verification.

Dependencies and integration: used by bulk load, ops, verify, snapshot replay, salvage diagnostics, and table creation. It depends on config macros (`TV`, `table_maxv`), global RNG, table type, and prefix length global `g.prefix_len_max`.

Risks and test signals: key format assumptions are shared with mirror verification and original-row filtering; changing suffix layout or minimum length can break parsing. Buffer sizing must account for largest configured keys/values plus prefixes. Reopen correctness depends on reading the exact saved length file.
