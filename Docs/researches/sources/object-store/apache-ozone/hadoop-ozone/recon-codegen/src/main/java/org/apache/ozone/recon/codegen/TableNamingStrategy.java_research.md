<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/codegen/TableNamingStrategy.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/codegen/TableNamingStrategy.java

## Purpose
Custom jOOQ generator strategy that gives generated table classes distinct names from POJOs.

## Important APIs, types, and functions
Extends `DefaultGeneratorStrategy` and overrides `getJavaClassName`. For `TableDefinition` in `Mode.DEFAULT`, it converts output table names to camel case after replacing spaces, hyphens, and dots with underscores, then appends `Table`.

## Control flow
Only table default-mode definitions receive the custom suffix. All other definitions and modes delegate to the superclass.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
Referenced by `JooqCodeGenerator` strategy configuration. It affects generated Recon class names and therefore downstream source imports.

## Risks and test signals
Changing the naming strategy is a source compatibility break for generated code users. Tests should generate schemas with names containing punctuation and verify table class names and POJO names do not collide.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/codegen/TableNamingStrategy.java -->
