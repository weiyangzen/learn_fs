# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ContainerImporter.java

Purpose: imports a replicated container tarball into local datanode storage, selecting a target volume, validating metadata/checksum state, unpacking through the appropriate container handler, and registering the container in the `ContainerSet`.

Important APIs and functions: `isAllowedContainerImport` rejects imports already in progress or containers already present. `importContainer` guards duplicate imports with `importContainerProgress`, reads the container descriptor via `TarContainerPacker`, verifies the container file checksum, sets the selected `HddsVolume`, clears data-scan timestamp, delegates actual import to `ContainerController.importContainer`, updates volume used space, overwrites missing-container tracking, and schedules an on-demand scan. `chooseNextVolume` asks the configured `VolumeChoosingPolicy` for a volume with reserved space. `getUntarDirectory` builds the `tmp/container-copy` work path under a volume. `getSpaceToReserve` uses actual replicate size when available, otherwise default SCM container size.

Control flow and state: the synchronized `HashSet` `importContainerProgress` is the process-local duplicate-import lock. The tarball is deleted in all paths. Failed imports mark the chosen volume failed through `StorageVolumeUtil.onFailure`.

Dependencies and integration: used by pull replication after download and by push replication request handling after stream completion. It depends on `ContainerDataYaml`, `ContainerUtils`, `TarContainerPacker`, volume selection, `ContainerController`, and `ContainerSet`.

Risks and test signals: space reservation must be balanced by callers, while used-space accounting happens here after successful import. Tests should cover duplicate push/pull races, tarball cleanup on all exceptions, checksum failure, descriptor parse failure, volume failure marking, actual-size reservation, and on-demand scan scheduling.
