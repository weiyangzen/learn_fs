## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconStorageConfig.java

Purpose: `ReconStorageConfig` specializes SCM storage metadata for Recon, including Recon identity and the SCM-issued certificate serial number.

Important APIs and types: extends `SCMStorageConfig` with node type `RECON`. Constants are `RECON_CERT_SERIAL_ID` and `RECON_ID`. Methods include `setReconCertSerialId`, `setReconId`, `getReconId`, `getNodeProperties`, `getReconCertSerialId`, and `unsetReconCertSerialId`.

Control flow: the constructor uses `ReconUtils.getReconDbDir` and Recon storage config keys to locate storage. During initialization, `getNodeProperties` ensures a Recon UUID exists and includes the cert serial ID if present. `setReconId` refuses changes after storage is initialized.

State and persistence: properties are stored in the SCM storage version file via inherited `getStorageInfo`. Persisted values include Recon UUID and optional certificate serial ID.

Dependencies and integration points: used by `ReconStorageContainerManagerFacade` to set cluster ID in `ReconContext` and by `ReconCertificateClient` to identify Recon to SCM's CA and retrieve existing certificate serial state.

Risks and edge cases: if `getReconId` is null, `getNodeProperties` generates a new UUID; operators must preserve the version file to keep a stable identity. Certificate serial management must stay consistent with certificate client callbacks.

Test signals: upgrade and initialization tests use the facade/storage path indirectly. Focused tests should cover UUID generation, initialized-state rejection, cert serial persistence/unset, and storage-dir resolution.
