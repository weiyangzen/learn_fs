# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ServiceInfoProvider.java

Purpose: `ServiceInfoProvider` assembles `ServiceInfoEx` responses for OM clients by combining the OM service list with cached CA certificate PEM strings in secure clusters. It also refreshes certificate cache state on root CA rotation.

Important APIs and types: Construction receives `SecurityConfig`, `OzoneManagerProtocol`, `CertificateClient`, and an optional testing skip flag. `provide()` returns `ServiceInfoEx`. Private helpers choose root CA certificates, select the newest certificate by `notAfter`, convert to PEM, and build a root-CA-rotation listener.

Control flow: In secure mode, the constructor reads root CA certs, falls back to all CA certs if root certs are empty, stores a newest PEM and a list of all PEMs, and registers a listener. The listener synchronizes on the provider, refreshes both fields, and completes a `CompletableFuture`. `provide` copies the cached fields under the same monitor and combines them with `om.getServiceList()`.

State and persistence behavior: Cached PEM strings are in-memory only. Persistent certificate material is owned by the certificate client and SCM/OM security subsystem.

Dependencies and integration points: It backs OM service-list RPCs used by clients that need service endpoints and trust roots. It depends on `CertificateClient`, `CertificateCodec`, and `ServiceInfoEx`.

Risks and test signals: Certificate conversion exceptions are wrapped as runtime exceptions during construction or listener execution. If there are no certs, the newest PEM is null and list may be empty. Tests should cover security disabled, skipped initialization, root-vs-all CA fallback, rotation listener refresh, defensive copy from `provide`, and PEM conversion failures.
