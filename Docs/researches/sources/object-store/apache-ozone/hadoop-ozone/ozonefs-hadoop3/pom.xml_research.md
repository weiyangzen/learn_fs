<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/pom.xml

## Purpose
Maven module for Hadoop 3-compatible shaded Ozone filesystem distribution.

## Important APIs, types, and functions
Builds artifact `ozone-filesystem-hadoop3`, skips tests in this module, depends on `ozone-filesystem-shaded`, SLF4J, reload4j provided, and Hadoop common provided. The dependency plugin unpacks the shaded jar during `prepare-package`; SpotBugs analyzes `org.apache.hadoop.fs.ozone.*`.

## Control flow
Package preparation unpacks shaded filesystem classes and resources into this module's classes, while local Hadoop 3 compatibility classes compile normally.

## State and persistence behavior
Only Maven target build outputs are created.

## Dependencies and integration points
This is the Hadoop 3 distribution wrapper that exposes stream capabilities and full Hadoop 3 APIs while embedding the shaded common Ozone FS implementation.

## Risks and test signals
Risks are dependency conflicts and missing tests in the module itself. Validation relies on compile/package, dependency analysis exceptions, SpotBugs, and downstream integration tests using the produced jar.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/pom.xml -->
