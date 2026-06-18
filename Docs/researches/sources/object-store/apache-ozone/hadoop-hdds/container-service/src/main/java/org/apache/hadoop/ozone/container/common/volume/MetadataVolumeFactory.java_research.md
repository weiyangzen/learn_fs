# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/MetadataVolumeFactory.java

Purpose: Factory for metadata/Ratis volumes.

Important APIs and types: Extends `StorageVolumeFactory`; normal creation wires configuration, usage factory, storage type, and volume set into `MetadataVolume.Builder`; failed creation marks the builder as failed.

Control flow: Unlike data and DB factories, it passes null datanode UUID and cluster ID into the superclass because metadata volumes are not formatted with datanode VERSION fields by Ozone.

State and persistence: No factory persistence. Built `MetadataVolume` handles usage and health-check state.

Dependencies and integration points: Selected by `MutableVolumeSet` for `META_VOLUME` and fed configured Ratis directories from `HddsServerUtil.getOzoneDatanodeRatisDirectory`.

Risks: This factory does not call `checkAndSetClusterID`, intentionally avoiding data-volume cluster validation. Tests should ensure metadata creation does not require cluster ID or datanode UUID.
