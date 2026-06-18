# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/DatanodeLayoutStorage.java

## Purpose
Datanode metadata layout storage wrapper responsible for locating and initializing datanode layout VERSION storage.

## Important APIs, Types, And Functions
Constructors initialize `Storage` for `NodeType.DATANODE` with metadata directory, datanode layout version directory, optional datanode ID, and layout version. Overrides `getCurrentDir`, `getNodeProperties`, and `setClusterId`.

## Control Flow
Startup constructs this class, checks its storage state, and initializes it if needed. Default layout version chooses the current max layout version unless an old `datanode.id` file exists without layout metadata, in which case it uses the initial layout version for upgrade compatibility.

## State And Persistence
Persistent state is the datanode layout VERSION directory under the Ozone metadata path. Cluster ID is stored in inherited storage info. No additional node properties are written.

## Dependencies And Integration Points
Depends on `Storage`, `ServerUtils.getOzoneMetaDirPath`, `HddsServerUtil.getDatanodeIdFilePath`, HDDS layout feature/version manager, and Ozone constants.

## Risks
The default layout heuristic is upgrade-sensitive: stale or misplaced datanode ID files can force initial layout. `setClusterId` mutates storage info without directly writing; caller must ensure persistence through storage lifecycle.

## Test Signals
Signals include fresh install defaulting to max layout, old-ID upgrade defaulting to initial version, VERSION initialization, cluster ID persistence, and current directory path correctness.
