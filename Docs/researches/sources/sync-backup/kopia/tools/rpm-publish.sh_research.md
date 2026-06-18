# sources/sync-backup/kopia/tools/rpm-publish.sh

Purpose: publishes Kopia RPMs to Google Cloud Storage-backed RPM repositories, signs new packages, prunes old unstable packages, regenerates repo metadata, and synchronizes results.

Control flow/APIs: validates package dir and `PACKAGES_HOST`, picks `stable testing` only for tagged CI releases otherwise `unstable`, creates `/tmp/rpm-publish`, `gsutil rsync`s existing distribution trees, prunes old RPMs per arch, classifies input RPM filenames by version and architecture, signs copies with `rpm --addsign`, regenerates metadata via `createrepo_c`, uploads with `gsutil rsync`, and disables caching on `repodata`.

State/persistence: mutates `/tmp/rpm-publish`, remote `gs://$PACKAGES_HOST/rpm`, and RPM signatures. It keeps only a few older unstable RPMs in working copies before sync.

Dependencies/integration: bash, `gsutil`, `rpm`, `createrepo_c`, GPG/RPM signing setup, package naming conventions, `PACKAGES_HOST`, and optional `CI_TAG`. Used in release publication.

Risks/test signals: filename regex controls release-channel classification, so packaging name drift can silently skip files. `delete_old_rpms` with empty globs can behave poorly. `WORK_DIR` is not cleared at start. Signing credentials and cloud permissions are external. Validation comes from package repository metadata and install tests downstream.
