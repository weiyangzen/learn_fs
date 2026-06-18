# sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_repair.py

## Purpose
This file tests mutable-file repair behavior for SDMF and MDMF files using the in-memory mutable test harness from `mutable/util.py`. It focuses on whether repair preserves, regenerates, or refuses share sets under no-op repair, missing-share repair, competing-version merge, read-cap-only repair, and empty-file repair cases.

## Important APIs, Types, And Functions
The main test class is `Repair`, combining `AsyncTestCase`, `PublishMixin`, and `ShouldFailMixin`. Helper methods include `get_shares`, `copy_shares`, `failIfSharesChanged`, `_test_whether_repairable`, `_test_whether_checkandrepairable`, and `get_roothash_for`. The tests exercise `MutableFileNode.check`, `repair`, `check_and_repair`, `get_servermap`, `download_version`, and `get_readonly`, plus `IRepairResults`, `ICheckAndRepairResults`, `Monitor`, `MODE_CHECK`, `unpack_header`, and `MustForceRepairError`.

## Control Flow
Tests are Twisted Deferred chains. They publish a file through `PublishMixin`, directly mutate `self._storage._peers`, invoke check or check-and-repair, and assert result interfaces and health flags. Merge tests use `publish_multiple` and `_set_versions` to create conflicting highest sequence-number versions, first proving ordinary repair refuses without `force=True`, then proving forced repair creates a new sequence number and downloadable best version.

## State, Persistence, And Dependencies
State is held in memory by `FakeStorage`, `self.old_shares`, and `self._copied_shares`; there is no disk persistence in this file. The test depends on Tahoe mutable layout parsing because it inspects share headers to compare sequence number, encoding parameters, segment size, and data length. It integrates with the repairer, servermap, mutable publisher, and read-only cap behavior.

## Risks And Test Signals
Important regressions caught here include repair changing share placement unexpectedly, treating too few shares as recoverable, allowing ambiguous merges without `force=True`, attempting mutable repair from a readcap, and losing empty-file private-key handling. Several tests still contain TODOs around deeper repair-result inspection, so they validate success and resulting content more than full diagnostic metadata.
