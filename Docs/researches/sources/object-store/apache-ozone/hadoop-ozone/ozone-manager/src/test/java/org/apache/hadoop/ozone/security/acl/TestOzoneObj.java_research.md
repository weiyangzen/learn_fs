<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneObj.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneObj.java

Purpose: focused unit test for `OzoneObjInfo` builder path-viewer behavior when volume, bucket, and key fields are present or null.

Important APIs and functions: `testGetPathViewer` and helper `getBuilder`. The helper creates a mocked `KeyManager`, an `OzonePrefixPathImpl`, and returns a builder with resource type `VOLUME`, store type `OZONE`, optional volume/bucket/key names, and the prefix path viewer.

Control flow: builds object info for complete, all-null, and volume-only path inputs, asserting expected volume name and non-null prefix path viewer each time.

State and persistence behavior: no persistence; all state is in-memory builder fields and a Mockito mock. The test guards builder behavior around nullable path components.

Dependencies and integration: `OzoneObjInfo`, `OzonePrefixPathImpl`, `KeyManager`, Mockito, and JUnit assertions. Risks are modest: this only checks non-null viewer plumbing and does not verify path traversal behavior. Test signal is that `OzoneObjInfo` should retain the provided viewer even for partially specified objects.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneObj.java -->
