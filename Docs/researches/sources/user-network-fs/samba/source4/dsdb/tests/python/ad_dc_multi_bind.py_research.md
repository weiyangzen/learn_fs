# sources/user-network-fs/samba/source4/dsdb/tests/python/ad_dc_multi_bind.py

Purpose: this compact performance/stability test repeatedly binds to the same AD DC and performs a base search, stressing connection setup, authentication, session creation, and cleanup behavior.

Important APIs/types/functions: `UserTests.test_1000_binds()` loops from 1 to 999, constructs a `SamDB(host, credentials=creds, session_info=system_session(lp), lp=lp)`, then searches `samdb.domain_dn()` with `SCOPE_BASE` and `attrs=["*"]`. The module also carries the same `ANCIENT_SAMBA` compatibility harness as the performance tests.

Control flow: parse options and `<host>`, initialize global `lp` and `creds`, normalize host to `tdb://` for files or `ldap://` for names, then execute the single test through `TestProgram` or the old subunit runner. Each iteration creates a fresh `SamDB` object; no connection pool is reused.

State and persistence behavior: the test does not intentionally modify directory state. Persistent impact should be limited to server-side bind/session accounting and logs.

Dependencies and integration points: depends on Samba credential parsing, `system_session`, `SamDB`, LDB base searches, and the Samba subunit runner. It is meaningful against LDAP and local TDB URLs, though bind cost differs substantially.

Risks: it can be slow or noisy against remote DCs and may expose resource leaks only indirectly. It does not assert per-bind latency or verify connection teardown; failures arise from bind/search exceptions.

Test signals: success means 999 consecutive bind/search cycles completed. Runtime and server resource usage are the practical performance indicators.
