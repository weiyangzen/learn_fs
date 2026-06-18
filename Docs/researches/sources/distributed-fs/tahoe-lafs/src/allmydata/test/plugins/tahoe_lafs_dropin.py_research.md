# sources/distributed-fs/tahoe-lafs/src/allmydata/test/plugins/tahoe_lafs_dropin.py

## Purpose
This plugin drop-in exposes test-only Tahoe-LAFS plugin objects for the test suite. It provides a fake endpoint parser and two dummy storage plugin instances that can be discovered through the plugin mechanism.

## Important APIs, Types, And Functions
The module imports `AdoptedServerPort` from `allmydata.test.common` and `DummyStorage` from `allmydata.test.storage_plugin`. It defines module-level objects `adoptedEndpointParser`, `dummyStoragev1`, and `dummyStoragev2`.

## Control Flow
There is no runtime control flow beyond module import. Plugin discovery imports the module and reads the exported objects.

## State, Persistence, And Dependencies
State is limited to the three module-level plugin objects. It depends on the test plugin support modules and is integrated by fixtures such as `UseTestPlugins` in `test_client.py`.

## Risks And Test Signals
The file is small but important for storage plugin tests. If names or module placement change, plugin discovery tests can fail even though the dummy storage implementation itself remains valid.
