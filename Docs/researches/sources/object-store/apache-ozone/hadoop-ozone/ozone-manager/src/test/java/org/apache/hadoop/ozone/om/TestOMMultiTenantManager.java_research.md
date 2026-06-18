# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOMMultiTenantManager.java

Purpose: Tests multi-tenancy feature gating and disabled-feature request rejection in `OMMultiTenantManager` and OM request dispatch.

Important APIs and types: `OMMultiTenantManager.checkAndEnableMultiTenancy`, `OzoneManager.checkS3MultiTenancyEnabled`, multi-tenancy OM request builders in `OMRequestTestUtils`, `OzoneManagerRatisUtils.createClientRequest`, `OzoneManagerRequestHandler.handleReadRequest`, `OMException.ResultCodes.FEATURE_NOT_ENABLED`, and Ranger/Kerberos OM config keys.

Control flow: `testMultiTenancyCheckConfig` builds an `OzoneConfiguration` incrementally and verifies the method fails until security, Kerberos or basic Ranger admin credentials, Ranger HTTPS address, and Ranger service are present. `testMultiTenancyRequestsWhenDisabled` mocks an OM with feature disabled, sends each multi-tenancy write request through Ratis request creation and each read request through the read handler, and expects feature-not-enabled results.

State and persistence: no OM DB persistence is used here. State is configuration and mocked OM security flags.

Dependencies and integration points: covers Ranger integration prerequisites, Hadoop security authentication settings, OM Ratis write request creation, and protobuf read request handling. It codifies backward compatibility by noting `getS3VolumeContext` falls back rather than failing when MT is disabled.

Risks and edge cases: configuration checker must not enable MT with partial Ranger credentials or missing security; write and read paths fail differently, via exception versus `OMResponse`. New multi-tenancy request types must be added to this test or may bypass the gate.

Test signals: runtime failures contain "Failed to meet", successful Kerberos/basic-auth configurations return true, write requests throw `OMException` with `FEATURE_NOT_ENABLED`, and read requests return unsuccessful protobuf responses with status `FEATURE_NOT_ENABLED`.
