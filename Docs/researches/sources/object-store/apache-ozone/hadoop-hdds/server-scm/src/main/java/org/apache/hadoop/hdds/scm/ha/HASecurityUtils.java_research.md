<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/HASecurityUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/HASecurityUtils.java

## Purpose

`HASecurityUtils` contains SCM HA security helpers for SCM certificate initialization, root CA creation, Ratis TLS setup, sending certificate-related requests through Ratis, and certificate classification.

## Important APIs, Types, and Functions

Important methods are `initializeSecurity`, overloaded `initializeRootCertificateServer`, `createSCMRatisTLSConfig`, `submitScmRequestToRatis`, `isSelfSignedCertificate`, and `isCACertificate`. Private `getScmSecurityClientWithFixedDuration` builds a bounded-wait SCM security client.

## Control Flow

Security initialization creates a `SecurityConfig`, obtains a failover SCM security client with adjusted retry count, constructs an `SCMCertificateClient`, and calls `initWithRecovery`, updating storage config when a certificate ID is received. Root CA initialization creates and initializes a `DefaultCAServer`. Ratis request submission builds a GRPC Raft client with TLS parameters and fixed retry policy, sends asynchronously, waits, and decodes `SCMRatisResponse`.

## State and Persistence Behavior

Certificate material and SCM cert serial ID are persisted by the certificate client and `SCMStorageConfig`. Ratis submission does not persist locally except through the replicated state machine handling the request.

## Dependencies and Integration Points

It integrates with HDDS security config, SCM security protocol failover proxies, certificate stores/clients, Default CA server, Ratis GRPC TLS, UGI, and SCM Ratis response decoding.

## Risks and Edge Cases

Retry count calculation depends on duration and retry interval units. TLS config is only returned when both security and gRPC TLS are enabled. Ratis request submission uses fixed retry constants and blocks on the future. Certificate ID persistence failures are wrapped in runtime exceptions from the callback.

## Test Signals

Tests should cover secure and insecure TLS config creation, root CA initialization defaults, retry-count adjustment for bounded init waits, certificate serial callback persistence, Ratis response decode path, and self-signed/CA certificate predicates.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/HASecurityUtils.java -->
