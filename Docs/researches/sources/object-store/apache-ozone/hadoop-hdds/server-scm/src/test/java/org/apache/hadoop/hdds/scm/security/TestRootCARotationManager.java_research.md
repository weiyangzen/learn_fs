# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/security/TestRootCARotationManager.java

## Purpose
`TestRootCARotationManager` validates root CA rotation scheduling, configuration validation, immediate versus scheduled rotation, leader-status reactions, and post-processing cleanup through stateful service storage.

## Important APIs, Types, and Functions
- `RootCARotationManager` construction, `start`, `stop`, `notifyStatusChanged`, and `setRootCARotationHandler` are exercised.
- Config keys include `HDDS_X509_CA_ROTATION_ENABLED`, `HDDS_X509_CA_ROTATION_CHECK_INTERNAL`, `HDDS_X509_CA_ROTATION_TIME_OF_DAY`, `HDDS_X509_RENEW_GRACE_DURATION`, `HDDS_X509_CA_ROTATION_ACK_TIMEOUT`, `HDDS_X509_EXPIRED_CERTIFICATE_CHECK_INTERVAL`, and `HDDS_X509_ROOTCA_CERTIFICATE_POLLING_INTERVAL`.
- `SCMCertificateClient`, `CertificateCodec`, `SelfSignedCertificate`, `StatefulServiceStateManager`, and `RootCARotationHandlerImpl` are important collaborators.
- `generateX509Cert` creates test CA certificates.

## Control Flow
Setup builds security configuration in a temp metadata directory, creates an SCM certificate client, and mocks `StorageContainerManager`, HA manager, sequence generator, security protocol server, SCM context, handler, and stateful service manager. Property tests construct managers with invalid and valid configs. Rotation tests create short-lived CA certs, set schedule times, start the manager, notify status changes, and capture logs to confirm rotation. Post-processing test simulates persisted rotation state, toggles leader status, and waits for post-processing logs and state deletion.

## State and Persistence Behavior
The test uses real certificate files under the temp security directory for one post-processing path and mocked stateful configuration storage for persisted rotation metadata. Manager state includes scheduled monitor task, post-processing flag, leader-active behavior, and root certificate server setup. The certificate client stores current CA certificate in memory.

## Dependencies and Integration Points
This test integrates SCM security, certificate codec, SCM HA/Ratis access, service manager, stateful service config, sequence IDs, and root certificate serving. It depends on log messages to observe asynchronous scheduler behavior.

## Risks and Edge Cases
Covered risks include invalid duration parsing, check interval longer than grace period, invalid time-of-day format, disabled auto-rotation ignoring invalid values, immediate rotation when scheduled time is too late for the grace window, scheduled rotation at a future time, leader change disabling monitor tasks, and deleting stateful config after post-processing completes.

## Test Signals
Strong signals are expected exceptions for bad config, counted log occurrences for a single scheduled rotation, immediate-rotation log checks, and verification that `deleteConfiguration` is called once after post-processing.
