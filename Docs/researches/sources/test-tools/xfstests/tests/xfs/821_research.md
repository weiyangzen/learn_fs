<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/821 -->
# sources/test-tools/xfstests/tests/xfs/821

Purpose: functional testing for realtime quota accounting and enforcement, including ownership transfers, hard limits, soft-limit timers, warnings, and bmbt block quota interactions.

Important APIs, types, and functions: uses `_scratch_supports_rtquota`, `_xfs_force_bdev realtime`, `report_rtusage`, xfs_quota `limit`, `timer`, `quota -u -r`, `xfs_io pwrite`, `_su` as the qa user, and `punch-alternating`.

Control flow: after mounting with user quota, it records realtime geometry, writes realtime extents as root and numeric users, changes ownership to move usage, tests hard and soft realtime block enforcement, extends grace periods, and checks bmbt quota during extent map punching.

State and persistence behavior: creates realtime files and quota records on scratch. Quota usage and timers persist until scratch cleanup.

Dependencies and integration points: depends on realtime support, user quota, qa user, punch-alternating helper, and xfs_quota realtime reporting.

Risks and test signals: delayed allocation affects when enforcement begins, so writes are synced. Signals are filtered quota reports, expected EDQUOT behavior, and final quota/bmap details.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/821 -->
