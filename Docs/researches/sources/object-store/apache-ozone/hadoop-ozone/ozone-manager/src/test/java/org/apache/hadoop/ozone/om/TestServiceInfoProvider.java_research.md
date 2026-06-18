# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestServiceInfoProvider.java

Purpose: Tests `ServiceInfoProvider`, which returns service list and CA certificate information to clients in secure and unsecure configurations.

Important APIs and types: `ServiceInfoProvider`, `ServiceInfoEx`, `OzoneManagerProtocol.getServiceList`, `SecurityConfig`, `CertificateClient`, `getAllRootCaCerts`, `registerRootCARotationListener`, certificate PEM encoding, and root CA rotation callback functions.

Control flow: base setup mocks OM service list as an empty list. In unsecure mode, provider returns no CA data. In secure mode, setup creates two self-signed certs, mocks all root certs, and constructs the provider. Tests call `provide` before and after a simulated root CA rotation listener callback with a newer cert list.

State and persistence: no files are persisted. Provider caches/currently tracks PEM root cert list and current CA certificate in memory. The cert client listener updates that state asynchronously via a returned completed future.

Dependencies and integration points: clients rely on this response to trust OM/SCM service endpoints. The provider bridges OM protocol service discovery, security config, and certificate rotation.

Risks and edge cases: unsecure mode must not expose CA fields; secure mode must choose the latest/active CA consistently; root CA rotation must update both single CA certificate and PEM list without recreating the provider.

Test signals: service list identity, null/empty CA fields in unsecure mode, PEM membership for root list, expected current PEM before and after rotation, and listener registration capture.
