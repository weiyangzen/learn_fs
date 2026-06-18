## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/scm/cert/RecoverSCMCertificate.java

Purpose: offline SCM repair command that restores missing local SCM certificate files from certificates persisted in the SCM RocksDB `VALID_SCM_CERTS` table, assuming private keys remain intact.

Important APIs and control flow: `--db` is required and SCM must be offline. `execute` normalizes the DB path, discovers the DB definition, locates the `VALID_SCM_CERTS` column-family definition and handle, opens RocksDB read-only, decodes all persisted certificates, selects the local host's sub-CA cert and the root-CA cert by subject-name prefixes, detects whether this host is root CA, and writes certificate PEM files using `CertificateCodec`. Helpers decode RocksDB rows, build cert paths with root included, and write root/subordinate/active certificate filenames.

State and dependencies: reads SCM DB without mutation, but writes certificate files under the configured SCM certificate locations. Depends on `SecurityConfig`, `SCMCertificateClient`, certificate codecs, DB definition discovery, and local hostname.

Risks and test signals: host-name subject matching can select nothing or the wrong cert if naming assumptions differ; caught RocksDB/certificate exceptions currently only log a generic error. No direct tests in this subset.
