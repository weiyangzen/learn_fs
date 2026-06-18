# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/multitenant/TestInMemoryMultiTenantAccessController.java

Purpose: binds the abstract multitenant access-controller conformance tests to the in-memory implementation selected by development configuration.

Important APIs/types: `InMemoryConfigurationForTesting`, `MutableConfigurationSource`, `OMMultiTenantManagerImpl.OZONE_OM_TENANT_DEV_SKIP_RANGER`, `MultiTenantAccessController.create`, and `InMemoryMultiTenantAccessController`.

Control flow: `createSubject()` constructs an in-memory mutable configuration, sets `OZONE_OM_TENANT_DEV_SKIP_RANGER` to true, invokes the static factory, and asserts the result is an `InMemoryMultiTenantAccessController`. The inherited test suite then exercises policy and role operations.

State and persistence behavior: backend state is in-memory and isolated to the controller instance returned per setup. There is no external Ranger server or persistent policy store. It still must emulate policy versioning, uniqueness checks, role IDs, labels, and role membership semantics expected by `MultiTenantAccessControllerTests`.

Dependencies and integration points: integrates with the controller factory and the dev-skip-Ranger branch used for tests and development. The class is intentionally package-private and has no direct tests of its own beyond inherited tests.

Risks: this subclass only proves factory routing and in-memory semantics. It does not cover HTTP/Ranger serialization or remote failure modes. If the factory condition changes, all inherited tests fail early because the instance assertion fails.

Test signals: confirms the in-memory backend is selected by configuration and satisfies the full abstract controller CRUD, role, label, version, and ACL conversion contract.
