# sources/user-network-fs/samba/source4/torture/drs/python/samba_tool_drs_no_dns.py

## Purpose
`samba_tool_drs_no_dns.py` tests building a joined DC database without DNS partitions and then adding ForestDNSZones and DomainDNSZones later through local DRS replication, `samba_upgradedns`, and `dbcheck`. It runs the same scenario for TDB and MDB backends.

## Important APIs, Types, And Functions
- `SambaToolDrsNoDnsTests` extends `drs_base.DrsBaseTestCase`.
- `_get_rootDSE()` returns both rootDSE and the connected SamDB.
- `_test_samba_tool_replicate_local_no_dns()` is parameterized by `self.backend`.
- Uses `BlackboxProcessError` handling because `dbcheck --fix` may return nonzero while still reporting checked/fixed entries.

## Control Flow
Each public test sets `self.backend` (`tdb` or `mdb`) and calls the shared helper. The helper joins a temporary DC with `--dns-backend=NONE`, full-sync replicates the escaped ForestDNSZones and DomainDNSZones NCs locally into the new database, verifies `msDS-hasMasterNCs` links are initially absent, runs `samba_upgradedns`, verifies those forward links appear, checks `msDS-NC-Replica-Locations` backlinks are initially absent, runs `samba-tool dbcheck --cross-ncs --fix --yes`, validates a clean cross-NC dbcheck, compares selected attributes with `ldapcmp`, verifies forward/back links for both DNS NCs, and demotes the temporary DC.

## State And Persistence Behavior
The test creates a temporary joined DC database and associated config under `self.tempdir`, adds DNS NCs after initial no-DNS provisioning, and repairs cross-NC references. The live domain sees a temporary DC account, which is removed through `domain demote --remove-other-dead-server`. Local runtime directories are removed in teardown.

## Dependencies And Integration Points
Integration spans `samba-tool domain join`, `samba-tool drs replicate --local --full-sync`, `samba_upgradedns`, `samba-tool dbcheck --cross-ncs`, `samba-tool ldapcmp`, LDB binary DN escaping, and both supported local backend stores. It validates interactions between NC replication and DNS upgrade/repair tools.

## Risks
The test assumes the environment can provision both TDB and MDB stores and can run DNS upgrade tooling. It depends on exact forward/backlink repair behavior and can fail if `dbcheck` output or return-code behavior changes. Demotion cleanup is required to avoid stale temporary DC objects.

## Test Signals
Signals include successful no-DNS join, successful local full-sync of both DNS NCs, zero `msDS-hasMasterNCs` and replica-location links before repair, one expected link/backlink after `samba_upgradedns` and `dbcheck`, clean cross-NC dbcheck, successful `ldapcmp` with filtered master/replica attributes, and successful demotion of the temporary DC.
