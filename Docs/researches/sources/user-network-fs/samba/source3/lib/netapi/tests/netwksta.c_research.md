# Research: sources/user-network-fs/samba/source3/lib/netapi/tests/netwksta.c

Purpose: integration tests for `NetWkstaGetInfo` workstation information queries. It checks basic WKSSVC/NetAPI support levels.

Important APIs/functions: `netapitest_wksta` iterates levels 100, 101, and 102, calls `NetWkstaGetInfo`, and tolerates status 124 for not-implemented behavior.

Control flow: simple fail-fast loop with a fresh output buffer pointer per level. It prints the level under test, treats nonzero/non-124 status as failure, and reports suite-level success/failure.

State and persistence: read-only target interaction. No workstation configuration is changed. Returned buffers are not explicitly freed in this test.

Dependencies/integration: depends on public `NetWkstaGetInfo` and shared test macros. The file is compiled into `netapitest` by `wscript_build`.

Risks: field contents are not validated, so mapping bugs can pass. Missing buffer free is a leak signal. The test assumes levels 100-102 are the relevant coverage set and does not exercise workstation set-info or domain/workgroup transitions.

Test signals: validate returned workstation name/domain/user fields where stable, free buffers, explicitly assert unsupported levels, and run against both standalone and domain-joined Samba configurations.
