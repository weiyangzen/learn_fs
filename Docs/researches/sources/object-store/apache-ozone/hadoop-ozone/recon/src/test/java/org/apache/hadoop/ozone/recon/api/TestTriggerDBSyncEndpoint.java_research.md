# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestTriggerDBSyncEndpoint.java

## Purpose
Tests `TriggerDBSyncEndpoint` for OM DB snapshot sync triggering and SCM DB snapshot sync trigger/status/cancel REST behavior.

## Important APIs, Types, And Functions
The tested endpoint methods are `triggerOMDBSync`, `triggerSCMDBSnapshotSync`, `getSCMDBSnapshotSyncStatus`, and `cancelSCMDBSnapshotSync`. Important collaborators are `OzoneManagerServiceProviderImpl`, `ReconStorageContainerManagerFacade`, `ReconUtils.createTarFile`, `DBCheckpoint`, `ReconTaskStatusUpdaterManager`, `ReconTaskStatusUpdater`, `ScmDbSnapshotTriggerResponse`, `ScmDbSnapshotStatusResponse`, `ScmDbSnapshotCancelResponse`, `ScmDbSnapshotSyncStatus`, and `ScmDbSnapshotSyncPhase`.

## Control Flow
`setUp` configures temporary Recon and OM snapshot directories, initializes OM metadata, creates a checkpoint tarball, mocks HTTP snapshot download and OM DB updates, starts an `OzoneManagerServiceProviderImpl`, and injects `TriggerDBSyncEndpoint`. The OM test calls `triggerOMDBSync` and expects a 200 `true` response. SCM tests instantiate the endpoint with mocked OM provider and Recon SCM facade and assert accepted, conflict, status, and cancel mappings from facade responses to HTTP responses.

## State And Persistence
Temporary local database directories, OM checkpoints, a tar snapshot file, and Recon SQL DB state are created. The service provider is started and uses mocked task status updater plumbing. SCM snapshot state is not persisted in these tests; it is represented by mocked facade response objects.

## Dependencies And Integration Points
The OM path integrates snapshot download, checkpoint packaging, OM protocol DB update polling, Recon context, task status updater management, and Guice injection. The SCM path checks REST translation of facade-level snapshot sync lifecycle states.

## Risks
The OM fixture opens an input stream from the tar file while stubbing `HttpURLConnection.getInputStream`, so stream lifetime and mock behavior are important. The test does not cover failed OM sync or SCM cancel rejection, but it anchors the key HTTP status mapping: accepted sync uses 202 and already-running sync uses 409.

## Test Signals
Signals include OM trigger returning status 200 with `true`, SCM trigger accepted returning 202 with `IN_PROGRESS`, SCM trigger conflict returning 409 with `accepted=false`, status reporting phase `DOWNLOADING_CHECKPOINT` and cancel allowance, and cancel returning 200 with `CANCELLED` status and phase.
