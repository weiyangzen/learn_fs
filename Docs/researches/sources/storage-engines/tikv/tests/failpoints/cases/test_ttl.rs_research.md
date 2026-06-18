# sources/storage-engines/tikv/tests/failpoints/cases/test_ttl.rs

See the grouped report section in `Docs/researches/groups/subset-b-008947_research.md` for the full source-aligned research. Summary: this file validates raw TTL for API v1 TTL and API v2 with `ttl_current_ts` fixed. It tests TTL file scanning, compaction-filter deletion, snapshot `get` and `get_key_ttl_cf`, iterator filtering, and `raw_batch_put`/`raw_get_key_ttl`. Key risks are expired latest versions, no-TTL records, timestamp-suffixed API v2 keys, and iterator seek behavior over hidden keys.
