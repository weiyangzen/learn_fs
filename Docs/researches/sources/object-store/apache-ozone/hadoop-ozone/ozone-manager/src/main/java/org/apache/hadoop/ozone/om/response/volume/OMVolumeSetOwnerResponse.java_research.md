<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMVolumeSetOwnerResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMVolumeSetOwnerResponse.java

Purpose: Persists a volume owner change by updating old/new owner volume lists and the volume's owner field.

Important APIs/types/functions: Extends `OMClientResponse`. Success constructor stores old owner, old owner list, new owner list, and updated `OmVolumeArgs`. The alternate constructor allows the no-change case where status is `OK` but success is false. It overrides `checkAndUpdateDB` to write only when status is `OK` and response success is true.

Control flow and persistence: Deletes or rewrites the old owner's user row depending on whether its list is empty, writes the new owner user row, and writes updated volume args to `VolumeTable[getVolumeKey(volume)]`.

Dependencies and integration: Used by set-volume-owner request handling.

Risks and test signals: The no-op same-owner case is special and must not mutate DB. Tests should cover same owner, old owner last volume, old owner with remaining volumes, new owner list update, volume owner field update, and failure no-op.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/volume/OMVolumeSetOwnerResponse.java -->
