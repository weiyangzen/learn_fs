<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/codegen/JooqCodeGenerator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/codegen/JooqCodeGenerator.java

## Purpose
Command-line utility that initializes Recon schemas in an embedded Derby database and runs jOOQ code generation for DAOs and POJOs.

## Important APIs, types, and functions
`JooqCodeGenerator` is Guice-injected with all `ReconSchemaDefinition` bindings. `initializeSchema` invokes each definition. `generateSourceCode` builds jOOQ JAXB configuration for Derby, schema `RECON`, DAOs, empty catalogs, `TableNamingStrategy`, and target package `org.apache.ozone.recon.schema.generated`. `LocalDataSourceProvider` creates and cleans up a temp Derby database.

## Control flow
`main` requires an output directory, builds an injector with `ReconSchemaGenerationModule` plus local datasource bindings, initializes schema, generates source code, and cleans up the Derby directory. SQL and generation failures are logged and rethrown as initializer errors.

## State and persistence behavior
Creates a temporary Derby database under `java.io.tmpdir` with a monotonic timestamp and deletes it after generation. Generated Java sources are written to the caller-provided output directory.

## Dependencies and integration points
Integrates Guice multibindings, Derby, jOOQ codegen, schema definitions, `SqlDbUtils`, and Recon generated-source build steps.

## Risks and test signals
Cleanup is skipped if an earlier fatal error exits before the final cleanup call. Static datasource initialization logs but does not stop immediately on DB creation failure. Tests should invoke `main` with a temp output, assert generated classes/tables, and verify temp DB cleanup on success and failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/codegen/JooqCodeGenerator.java -->
