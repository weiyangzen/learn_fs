# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/RootCaRotationPoller.java

## Purpose

`RootCaRotationPoller` periodically asks SCM for all root CA certificates and triggers registered processors when SCM knows root CAs that the client does not.

## Important APIs, Types, and Functions

The constructor captures polling interval, initial known root cert set, SCM security client, thread name prefix, processor list, scheduled executor, and an atomic renewal-error flag. `pollRootCas` fetches PEM roots, converts to X.509, computes unknown certs, logs IDs, runs all processors with `CompletableFuture.allOf`, and updates `knownRootCerts` only if processors complete successfully and no renewal error was signaled. `addRootCARotationProcessor`, `run`, `close`, and `setCertificateRenewalError` control lifecycle.

## Control Flow

`run` schedules `pollRootCas` at fixed rate with zero initial delay. Each poll is a fetch/compare/notify/update cycle. Processors receive the full SCM root list, not just the new certificates.

## State and Persistence Behavior

State is in-memory only: known root certs and renewal-error flag. Persistence of new root certificates is delegated to processors such as `DefaultCertificateClient` renewal handlers.

## Dependencies and Integration Points

It integrates `SCMSecurityProtocolClientSideTranslatorPB.getAllRootCaCertificates`, `OzoneSecurityUtil.convertToX509`, scheduled executors, and certificate-client rotation processors.

## Risks and Edge Cases

The processor list is an unsynchronized `ArrayList`; adding processors while polling can race. `pollingInterval.getSeconds()` truncates sub-second durations. Exceptions inside asynchronous processors are handled by `whenComplete`, but update happens asynchronously after `pollRootCas` returns.

## Test Signals

Test no-op when cert sets match, processor invocation for new roots, known-set update only after successful processors, renewal-error suppression, SCM fetch IOException handling, close shutdown, and concurrent listener registration behavior.
