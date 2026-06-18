# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMCertStore.java

Purpose: `SCMCertStore` persists certificates issued by SCM CA into SCM metadata tables. SCM certificates are stored in both the generic valid cert table and the SCM-specific valid cert table.

Important APIs and types: It implements `CertificateStore`. Methods include `storeValidCertificate`, `storeValidScmCertificate`, `checkValidCertID`, `removeAllExpiredCertificates`, `getCertificateByID`, `listCertificate`, and `reinitialize`. The builder wraps the store in a Ratis proxy using `CertificateStoreInvoker`.

Control flow: Store operations take a `ReentrantLock`. For SCM role certificates, `storeValidCertificate` delegates to `storeValidScmCertificate`, which writes both tables in a single batch operation. Non-SCM roles write only the generic valid cert table. Expired removal iterates valid and valid-SCM tables, queues deletes in one batch, and commits.

State and persistence behavior: Durable state lives in `SCMMetadataStore` tables keyed by certificate serial number. Batch operations ensure SCM certs are written consistently across both tables. `reinitialize` swaps the underlying metadata store during state-machine reload.

Dependencies and integration points: It integrates X.509 certificate authority code, SCM metadata tables, Ratis proxy invocation, and root CA rotation. `RootCARotationManager` uses it to persist new root certificates and remove expired certs.

Risks: The TODO notes that role-specific listing is only implemented for SCM versus generic roles. Expired certificates may appear in both valid and SCM tables, so removal returns both entries. Locking is local to this store instance; replicated invocation ordering is handled by Ratis proxy.

Test signals: Tests should verify duplicate serial rejection, SCM cert dual-table writes, non-SCM generic writes, batch atomicity, expired removal from both tables, list pagination with start ID zero handling, reinitialization, and proxy builder behavior.
