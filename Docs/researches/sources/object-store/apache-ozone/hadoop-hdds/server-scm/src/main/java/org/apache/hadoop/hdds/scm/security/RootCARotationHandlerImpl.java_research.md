# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/security/RootCARotationHandlerImpl.java

Purpose: This class implements the Ratis-applied root CA rotation commands for each SCM. It reacts to leader prepare/commit messages, coordinates local sub-CA certificate directory switching, tracks prepare acknowledgements, and reloads the SCM certificate client after commit.

Important APIs and types: It implements `RootCARotationHandler` and uses `StorageContainerManager`, `SCMCertificateClient`, `SecurityConfig`, `RootCARotationManager`, `SCMRatisServer`, and `RootCARotationHandlerInvoker`. Runtime state includes `newScmCertIdSet`, `newSubCACertId`, `newRootCACertId`, and the computed `newSubCAPath`.

Control flow: `rotationPrepare` skips already-applied root certs, resets ack state, records the new root ID, and schedules sub-CA preparation. `rotationPrepareAck` counts unique SCM certificate IDs only while the rotation manager is running and this root ID matches. `rotationCommit` atomically moves current sub-CA material to a backup directory, moves the new directory into the current path, and persists the new SCM certificate serial ID. `rotationCommitted` reloads keys/certs, deletes the backup directory, and clears the new sub-CA ID.

State and persistence behavior: Persistence is filesystem-heavy. It uses atomic directory moves for current, backup, and next certificate directories and persists the current SCM certificate serial ID through `SCMStorageConfig.persistCurrentState()`. Ack sets are in-memory and reset after rotation.

Dependencies and integration points: The builder wraps the implementation in a Ratis proxy handler, so calls participate in SCM HA replication. It depends on the rotation manager for skip decisions and task scheduling.

Risks: Directory moves are shutdown-triggering failure points. The class calls `scm.shutDown` on IO failures but continues through surrounding method structure, so callers must treat shutdown as terminal. `newScmCertIdSet` is a plain `HashSet`; method execution is expected to be serialized by Ratis/manager context rather than arbitrary concurrent callers.

Test signals: Tests should cover prepare reset, duplicate ack collapse, skip on already-current root cert, successful directory swap, persisted serial ID, certificate reload, backup cleanup, and builder proxy creation.
