# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestHsyncGenerator.java

Purpose: Non-HA integration test for Freon `HsyncGenerator`, ensuring the generator command succeeds against an OFS bucket path in a mini cluster.

Important APIs, types, and functions: Implements `NonHATests.TestCase`. Uses `HsyncGenerator`, picocli `CommandLine`, `OzoneClient`, `ObjectStore`, `OzoneVolume`, `OZONE_OFS_URI_SCHEME`, and `OZONE_OM_ADDRESS_KEY`.

Control flow: The test creates a random volume and `bucket1`, constructs an OFS root path of the form `ofs://<om-address>/<volume>/<bucket>/`, executes the generator with 8 bytes per write, 64 writes per transaction, five threads, and 100 operations, then asserts exit code zero.

State and persistence behavior: Creates real volume/bucket namespace and writes data through hsync workload operations. The test does not inspect generated files afterward; persistence is implied by command success.

Dependencies and integration points: Covers Freon CLI parsing, OFS URI handling, hsync write path, and Ozone client/object-store setup.

Risks: Exit-code-only validation may miss subtle durability or content issues. Workload timing can vary with cluster performance. The path depends on OM address config being populated.

Test signals: The generator command must return exit code `0`.
