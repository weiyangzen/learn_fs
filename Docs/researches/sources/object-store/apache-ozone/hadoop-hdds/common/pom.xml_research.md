## sources/object-store/apache-ozone/hadoop-hdds/common/pom.xml

**Purpose:** Maven module descriptor for `hdds-common`, declaring its artifact identity, dependencies, resource filtering, generated version info, static-analysis filter, config annotation processing, import restrictions, and OS build extension.

**Important APIs/types/functions:** The module inherits from `hdds-hadoop-dependency-client` version `2.3.0-SNAPSHOT`, publishes `org.apache.ozone:hdds-common`, and packages a jar. Dependencies include Jackson, Guava, protobuf, re2j, commons libraries, OpenTelemetry, Hadoop common, HDDS config/interface client modules, Ratis clients/transports/metrics, Bouncy Castle, SLF4J, and test utilities. Build resources filter only `hdds-version-info.properties`. `hadoop-maven-plugins:version-info` runs in `generate-resources` over sibling Java/proto sources. SpotBugs uses `dev-support/findbugsExcludeFile.xml`. `maven-compiler-plugin` configures `hdds-config` as an annotation processor and invokes `ConfigFileGenerator` with `-AartifactId=${project.artifactId}`. The enforcer override bans `org.kohsuke.MetaInfServices` imports while allowing selected processors. `os-maven-plugin` is a build extension.

**Control flow:** Maven evaluates parent dependency management, resolves dependencies, generates version metadata before resources are packaged, runs annotation processing during compilation, and applies SpotBugs/enforcer rules during configured lifecycle phases.

**State and persistence:** Persistent build metadata. Generated version/config resources are build outputs, not checked-in runtime state.

**Dependencies and integration points:** Central integration point between HDDS common Java code, generated config docs/resources, SpotBugs, Hadoop/Ratis/protobuf/OpenTelemetry dependencies, and downstream modules consuming `hdds-common`.

**Risks:** Dependency breadth makes convergence and transitive conflicts important. Annotation processor configuration is required for config generation; breaking it can silently affect generated config artifacts. Resource filtering is intentionally narrow to avoid accidental token substitution.

**Test signals:** Maven build, compiler annotation processing, enforcer, and SpotBugs runs validate this file. Unit tests in dependent modules indirectly validate dependency availability.
