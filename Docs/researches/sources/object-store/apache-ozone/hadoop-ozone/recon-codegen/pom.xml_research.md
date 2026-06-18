<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/pom.xml

## Purpose
Maven module for Recon jOOQ code generation support.

## Important APIs, types, and functions
Builds artifact `ozone-reconcodegen`, skips tests, and depends on Guice, Commons IO, Derby, Hadoop common, jOOQ runtime/codegen/meta, SLF4J, Spring TX, and provided JAXB API. Compiler annotation processing is disabled.

## Control flow
The module compiles code generation and schema definition classes used to create generated Recon DAO/POJO sources from programmatic schema definitions.

## State and persistence behavior
Build output is under `target`; runtime codegen creates temporary Derby databases and generated source directories when invoked.

## Dependencies and integration points
Supports the Recon module by producing jOOQ classes for schema tables. It integrates with Guice multibindings and Derby metadata.

## Risks and test signals
Tests are skipped, so regressions surface during downstream code generation or Recon compilation. Build validation should run the generator against a temp output and compile generated sources.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/pom.xml -->
