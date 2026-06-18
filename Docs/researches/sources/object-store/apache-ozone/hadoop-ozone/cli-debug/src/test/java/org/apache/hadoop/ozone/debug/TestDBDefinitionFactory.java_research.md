# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/test/java/org/apache/hadoop/ozone/debug/TestDBDefinitionFactory.java

Purpose: `TestDBDefinitionFactory` verifies that debug DB definition lookup returns the expected `DBDefinition` implementation for OM, SCM, Recon, and datanode schema versions.

Important APIs and types: It uses `DBDefinitionFactory.getDefinition`, `setDnDBSchemaVersion`, `OMDBDefinition`, `SCMDBDefinition`, `ReconSCMDBDefinition`, `ReconDBDefinition`, `DatanodeSchemaOneDBDefinition`, `DatanodeSchemaTwoDBDefinition`, and `DatanodeSchemaThreeDBDefinition`.

Control flow: A single test requests definitions by DB name and by datanode DB path/config after setting schema version to V2, V1, and V3, asserting the returned class each time.

State and persistence behavior: It uses no real DB. It does mutate global/static datanode schema selection in `DBDefinitionFactory`.

Dependencies and integration points: This protects the `ozone debug db` family of commands that need the right column-family definitions for each DB flavor.

Risks: Static schema version state can leak to later tests if not reset elsewhere. The datanode path is `/tmp/test-container.db` but no filesystem access is expected.

Test signals: Exact class identity for all supported database definition cases.
