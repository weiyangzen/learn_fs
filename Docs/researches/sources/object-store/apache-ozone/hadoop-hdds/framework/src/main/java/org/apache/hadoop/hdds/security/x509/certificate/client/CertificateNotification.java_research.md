# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/CertificateNotification.java

## Purpose

`CertificateNotification` is a callback interface for consumers that need to react when a `CertificateClient` renews its certificate.

## Important APIs, Types, and Functions

`notifyCertificateRenewed(CertificateClient certClient, String oldCertId, String newCertId)` is the single method.

## Control Flow

`DefaultCertificateClient` invokes registered receivers after resetting/reloading local certificate state during renewal.

## State and Persistence Behavior

No state or persistence is defined by this interface. Implementations such as reloadable key/trust managers update their own in-memory state.

## Dependencies and Integration Points

It integrates certificate-client renewal events with TLS manager reloads and any service-specific consumers.

## Risks and Edge Cases

Callbacks run synchronously inside notification iteration in the default client. Slow or throwing receivers can affect renewal follow-up unless callers guard their implementations.

## Test Signals

Register fake receivers and assert they receive old/new IDs during `reloadKeyAndCertificate`; test multiple receivers and receiver failure behavior in the concrete notifier.
