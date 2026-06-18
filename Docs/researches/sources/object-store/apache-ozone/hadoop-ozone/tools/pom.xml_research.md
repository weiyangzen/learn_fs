# sources/object-store/apache-ozone/hadoop-ozone/tools/pom.xml

## Purpose
Maven module descriptor for `ozone-tools`, packaging CLI utilities such as Ozone FS shell, getconf, genconf, local runtime config, Ratis shell wrapper, logging, and completion support.

## Important APIs, types, and functions
Defines artifact `org.apache.ozone:ozone-tools:2.3.0-SNAPSHOT`, jar packaging, dependencies on Hadoop common, HDDS CLI/config/common, Ozone common/filesystem, Ratis common/shell/proto, picocli, Reflections, reload4j, JAXB, and test jars. Build plugins configure SpotBugs, annotation processors, and enforcer import restrictions.

## Control flow
During build, compiler processors generate MetaInfServices and picocli native-image metadata. SpotBugs consumes the module exclude filter. Enforcer overrides root banned imports and restricts selected annotation-related imports.

## State and persistence behavior
The POM controls produced artifacts and generated metadata, not runtime persistence. Runtime-scoped dependencies shape the classpath for shell execution.

## Dependencies and integration points
It ties tools code to HDDS/Ozone libraries, Hadoop FsShell, Ratis shell, and CLI registration infrastructure.

## Risks and edge cases
Dependency scopes are important: moving runtime dependencies to compile or removing annotation processors can break service discovery/autocomplete/native metadata. Enforcer bans protect layering around config annotations and OM validation annotations.

## Test signals
Signals are successful Maven compile/test/static-analysis runs and availability of expected CLI classes in the assembled classpath.
