# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/resources/core-site.xml

Purpose: This test `core-site.xml` provides proxy-user permissions for integration tests.

Important APIs and types: It is a Hadoop XML configuration resource with `hadoop.proxyuser.proxyuser.users`, `hadoop.proxyuser.proxyuser.groups`, and `hadoop.proxyuser.proxyuser.hosts`, all set to wildcard values.

Control flow: There is no executable code. Hadoop configuration loading makes these keys available to tests and services.

State and persistence behavior: Static configuration only; it does not persist runtime state.

Dependencies and integration points: It supports tests involving proxy user impersonation by allowing the test user named `proxyuser` to proxy any user, group, and host. It is loaded alongside other site XML resources in the integration-test classpath.

Risks: Wildcard proxy settings are appropriate for test isolation but insecure for production. Tests depending on proxy-user behavior may fail if this file is not on the classpath.

Test signals: The signal is successful authorization of proxy-user scenarios that require permissive users, groups, and hosts.
