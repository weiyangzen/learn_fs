<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/ReconSchemaGenerationModule.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/ReconSchemaGenerationModule.java

## Purpose
Guice module that registers all Recon schema definitions used by the jOOQ generator.

## Important APIs, types, and functions
Extends `AbstractModule`. In `configure`, creates a `Multibinder<ReconSchemaDefinition>` and adds bindings for `UtilizationSchemaDefinition`, `ContainerSchemaDefinition`, `ReconTaskSchemaDefinition`, `StatsSchemaDefinition`, and `SchemaVersionTableDefinition`.

## Control flow
When Guice builds the injector, all bindings contribute to the injected set consumed by `JooqCodeGenerator`.

## State and persistence behavior
No state is stored in the module. Persistence happens through bound schema definitions.

## Dependencies and integration points
This is the discovery point for codegen schema classes. New schema definitions are invisible to generation until bound here.

## Risks and test signals
Forgetting a binding silently omits tables from generated jOOQ code. Tests should assert the bound set contains every expected definition and that generated output includes each table.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/ReconSchemaGenerationModule.java -->
