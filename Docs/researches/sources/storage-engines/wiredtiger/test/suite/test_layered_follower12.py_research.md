<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower12.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_follower12.py

Purpose: verifies timestamps on follower ingest-table records are not cleared merely because they become globally visible.

Important APIs/types/functions: uses follower role config, precise checkpoint settings, timestamped insert at ts=10, `conn.set_timestamp(stable=20,oldest=20)`, debug eviction session, and role step-up through `conn.reconfigure('disaggregated=(role="leader")')`.

Control flow: the follower creates a layered table, writes key `'a'` at timestamp 10, advances stable/oldest past it, evicts the page through a debug eviction cursor, steps up to leader, and reads key `'a'`.

State and persistence behavior: even though the record is globally visible and evicted, its timestamp metadata must remain valid enough for step-up/drain semantics; clearing it would risk losing or mis-ordering the ingest content.

Dependencies/integration points: integrates ingest eviction, global visibility, timestamp preservation, and follower-to-leader role transition. Risks are narrow coverage with a single key. Test signal is successful read of `'b'` after step-up.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower12.py -->
