# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/InodeMetadataRocksDBCheckpoint.java

## Purpose
`InodeMetadataRocksDBCheckpoint` represents a RocksDB checkpoint layout that reconstructs inode-based metadata snapshots using hardlinks described by a `hardLinkFile`. It optimizes disk use and normalizes v1/v2 checkpoint layouts.

## Important APIs and Types
Constructors accept a checkpoint path and optional `deleteSourceFiles` flag. `installHardLinks` reads hardlink mappings and creates links. `moveActiveDbFilesToOmDbIfNeeded` moves root-level active DB files into `om.db` for v1 format. `cleanupCheckpoint` deletes the checkpoint directory.

## Control Flow and State
Construction stores the location/timestamp, installs hardlinks, then normalizes active DB file placement. `installHardLinks` reads lines split by `OzoneConsts.HARDLINK_SEPARATOR`, creates parent directories, creates hardlinks from source to target inside the checkpoint tree, deletes the hardlink file, and optionally deletes source files. Malformed lines are skipped with warnings.

## Persistence, Dependencies, and Integration
This class mutates checkpoint directories and uses filesystem hardlinks. It depends on Apache Commons IO `FileUtils`, Java NIO `Files`, `HddsServerUtil.OZONE_RATIS_SNAPSHOT_COMPLETE_FLAG_NAME`, and Ozone constants. It implements `DBCheckpoint` for snapshot install flows.

## Risks and Test Signals
Hardlink creation can fail across filesystems or if targets already exist. Deleting source files in v2 mode is destructive but intended after links exist. Tests should cover missing hardlink file, malformed mappings, parent directory creation, v1 active-file movement, completion flag preservation, source deletion failures, cleanup deletion, and latest sequence returning `-1`.
