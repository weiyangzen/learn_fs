<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ServiceInfoEx.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ServiceInfoEx.java

## Purpose

`ServiceInfoEx` extends service discovery with CA certificate data so clients can discover service endpoints and TLS trust material together.

## Important APIs, Types, And Functions

The class implements `CACertificateProvider`. It exposes `getServiceInfoList`, `getCaCertificate`, `getCaCertPemList`, and `provideCACerts`.

## Control Flow, State, And Persistence

The object is an immutable-ish response wrapper. `provideCACerts` prefers the PEM list; if the list is empty, it falls back to the single PEM string, rejecting the case where both are unavailable. It then converts PEM strings to `X509Certificate` objects.

## Dependencies And Integration Points

It depends on `ServiceInfo`, HDDS `CACertificateProvider`, `OzoneSecurityUtil`, and Java certificate APIs. It integrates with secure OM clients, gRPC transport CA setup, and service discovery responses.

## Risks And Test Signals

An empty single PEM is intentionally ignored for tests, which can leave `caCertPems` null before conversion depending on inputs. Tests should cover multiple CA certs, legacy single cert, null/empty cert data, malformed PEM, and secure client bootstrap.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/ServiceInfoEx.java -->
