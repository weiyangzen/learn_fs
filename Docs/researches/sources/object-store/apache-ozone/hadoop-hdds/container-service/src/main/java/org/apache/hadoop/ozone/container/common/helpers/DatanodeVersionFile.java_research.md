<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/DatanodeVersionFile.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/DatanodeVersionFile.java

Purpose: small value object and IO helper for datanode volume `VERSION` files.

Important APIs and control flow: the constructor captures storage ID, cluster ID, datanode UUID, creation time, and layout version. `createProperties` maps those values to `OzoneConsts` property keys. `createVersionFile` writes the properties to the supplied file through `IOUtils.writePropertiesToFile`; `readFrom` reads an existing file into `Properties` via `IOUtils.readPropertiesFromFile`.

State and persistence: this class owns the on-disk property format for datanode volume identity. It does not validate values beyond storing them as strings, so callers are responsible for semantic checks such as UUID shape, cluster matching, and layout compatibility.

Dependencies and integration: `ContainerUtils.recoverDatanodeDetailsFromVersionFile` reads this format when the datanode ID file is corrupt or unavailable. Volume initialization and upgrade code can use it to persist storage identity.

Risks and test signals: tests should verify exact property names, round-trip read/write, missing keys, invalid numeric layout/ctime strings handled by consumers, and IO failures. Since `readFrom` returns raw `Properties`, downstream code must not assume all required fields are present.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/DatanodeVersionFile.java -->
