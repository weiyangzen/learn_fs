<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/install-maven/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/install-maven/action.yml

Purpose: Installs a pinned Maven distribution for Java PMD/site CI jobs.

Important APIs/types/functions: downloads `apache-maven-3.9.11-bin.tar.gz`, extracts it, appends `M2_HOME` to `GITHUB_ENV`, and appends the Maven bin directory to `GITHUB_PATH`.

Control flow: a single bash step performs download, extraction, and environment export.

State and persistence behavior: writes the Maven tree into the current workspace and updates job environment files for later steps.

Dependencies and integration points: used by `build-linux-java-pmd` in `pr-jobs.yml`; integrates with `make jpmd` and Maven-generated reports under `java/target`.

Risks: uses `--no-check-certificate`, reducing TLS validation. Archive URL availability and lack of checksum verification are supply-chain and reliability risks.

Test signals: later PMD job success and the presence of uploaded `pmd.xml` and Maven site artifacts.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/install-maven/action.yml -->
