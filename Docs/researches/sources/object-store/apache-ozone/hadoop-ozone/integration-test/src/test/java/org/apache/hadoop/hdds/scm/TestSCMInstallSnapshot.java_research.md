# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSCMInstallSnapshot.java

## Purpose

`TestSCMInstallSnapshot` validates local SCM checkpoint download and installation behavior outside the full HA follower-catch-up path. It ensures SCM can create a DB checkpoint and install it through snapshot utilities.

## Important APIs, Types, And Functions

The class uses `MiniOzoneCluster`, `StorageContainerManager`, `DBCheckpoint`, SCM metadata store APIs, and temporary directories. Tests are `testDownloadSnapshot`, `downloadSnapshot`, and `testInstallCheckPoint`.

## Control Flow

Setup starts a cluster. `testDownloadSnapshot` obtains a checkpoint and checks it is valid. `testInstallCheckPoint` downloads a checkpoint, installs it into a target location, and validates the installed checkpoint contents/state.

## State And Persistence Behavior

The test snapshots SCM RocksDB metadata and materializes checkpoint files on disk. Installation copies or restores checkpoint contents but does not represent normal client data mutation.

## Dependencies And Integration Points

It integrates SCM metadata store checkpoint creation, DB checkpoint lifecycle, local filesystem temp paths, and snapshot installation helper code used by HA catch-up.

## Risks And Test Signals

Failures reveal checkpoint corruption, missing files, bad cleanup/lifecycle handling, or restore-path incompatibility. Disk-path handling is the main edge case.
