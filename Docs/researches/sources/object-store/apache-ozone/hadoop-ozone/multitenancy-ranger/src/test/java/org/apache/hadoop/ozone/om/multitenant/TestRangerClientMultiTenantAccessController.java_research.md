# sources/object-store/apache-ozone/hadoop-ozone/multitenancy-ranger/src/test/java/org/apache/hadoop/ozone/om/multitenant/TestRangerClientMultiTenantAccessController.java

## Purpose

This test class adapts the shared `MultiTenantAccessControllerTests` suite to the real `RangerClientMultiTenantAccessController` implementation.

## Important APIs and Types

- Extends `MultiTenantAccessControllerTests`.
- Overrides `createSubject()` to build an in-memory configuration and return `MultiTenantAccessController.create(conf)` asserted as `RangerClientMultiTenantAccessController`.
- Annotated `@Unhealthy("Requires a Ranger endpoint")`.

## Control Flow

The test sets JVM SSL truststore and Kerberos config system properties, enables Kerberos debug logging, uses default Kerberos name rules, fills Ranger HTTPS address, Ranger service name, OM Kerberos principal, and keytab path, optionally documents SIMPLE auth settings as commented code, raises RangerClient logging to DEBUG, and creates the subject through the factory.

## State and Persistence

It mutates global JVM system properties and Kerberos name rules, which can affect other tests in the same JVM. It does not persist application data except whatever the inherited tests may create through a live Ranger endpoint.

## Dependencies and Integration Points

It depends on in-memory HDDS configuration, Hadoop Kerberos utilities, `GenericTestUtils`, `RangerClient` logging, and the abstract multitenancy test suite. It is intended for manual or unhealthy test lanes with a reachable Ranger server.

## Risks and Edge Cases

Hard-coded placeholder paths and localhost Ranger URL mean the test fails without environment-specific setup. Global Kerberos/SSL mutations can leak. The test currently covers Kerberos path only; SIMPLE auth is noted but not active.

## Test Signals

When enabled in a configured environment, it signals that factory creation, Ranger authentication setup, and inherited CRUD tests work against real Ranger. In normal CI, the `@Unhealthy` marker means it likely does not protect routine builds.
