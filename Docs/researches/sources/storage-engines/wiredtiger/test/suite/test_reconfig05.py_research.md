# sources/storage-engines/wiredtiger/test/suite/test_reconfig05.py

Purpose: tests that connection reconfiguration parses nested structs without the `=` separator form issues, specifically around cache size and log OS cache dirty percentage.

Important APIs and types: `self.session.create`, `self.conn.reconfigure`, `log=(enabled)`, and config strings `cache_size=1GB`, `log=(os_cache_dirty_pct=30/50)`.

Control flow: it creates a simple string-key/string-value table, then applies three connection reconfiguration strings: cache only, cache plus nested log option, and nested log option only.

State and persistence behavior: minimal table state is created to ensure an initialized connection/table context. The real target is configuration parsing and live mutation.

Dependencies and integration points: connection config parser, log configuration parser, cache manager, and reconfigure path.

Risks: successful parsing does not validate runtime side effects of `os_cache_dirty_pct`.

Test signals: all three reconfiguration calls return successfully.
