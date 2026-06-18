# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/reconfig/ReconfigurationTestBase.java

## Purpose
`ReconfigurationTestBase` is a shared abstract base for non-HA integration tests that validate live reconfiguration handlers for Ozone services.

## Important APIs, Types, and Functions
The class implements `NonHATests.TestCase`, captures the current short username via `UserGroupInformation`, requires subclasses to provide `getSubject()`, and exposes `assertProperties(ReconfigurationHandler, Set<String>)`. The assertion checks both `getReconfigurableProperties()` and sorted `listReconfigureProperties()`.

## Control Flow, State, and Persistence
At `@BeforeAll`, the current user is stored for admin-list tests. `assertProperties` verifies that the handler's set of reconfigurable properties and public list output match the expected set. No persistent state is changed by the base class.

## Dependencies and Integration Points
It integrates JUnit per-class lifecycle, the `NonHATests` cluster-injection contract, Hadoop `ReconfigurationHandler`, and current-user lookup. Subclasses for DN, OM, and SCM use it to share property-list validation and current-user expectations.

## Risks and Test Signals
Risk is mostly in expected property-set drift: added or removed reconfigurable keys must be reflected in subclass tests. The base provides a clean signal that handler introspection and list ordering are consistent.
