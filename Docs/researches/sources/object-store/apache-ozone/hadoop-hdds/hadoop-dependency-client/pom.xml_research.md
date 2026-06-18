# sources/object-store/apache-ozone/hadoop-hdds/hadoop-dependency-client/pom.xml

Purpose: Maven BOM-style module defining the pruned Hadoop client dependency surface for HDDS/Ozone clients.

Important APIs/types/functions: Maven `project`, parent `org.apache.ozone:hdds:2.3.0-SNAPSHOT`, artifact `hdds-hadoop-dependency-client`, packaging `pom`, and `dependencyManagement` entry for `org.apache.hadoop:hadoop-common`.

Control flow: During Maven dependency resolution, this POM manages `hadoop-common` at `${hadoop.version}` while excluding many transitive dependencies such as logging stacks, Jackson databind, Jersey, Guava, Curator, ZooKeeper, Jetty, Netty native epoll, servlet APIs, Avro, and Snappy.

State and persistence behavior: Build metadata only; no runtime state. It affects generated dependency graphs and downstream client classpaths.

Dependencies and integration points: Integrates with the parent HDDS build, Maven dependency management, Hadoop client libraries, and downstream modules importing this dependency POM.

Risks: The exclusion list is large and includes a duplicate Curator wildcard. Excluding broad artifacts can cause runtime `ClassNotFoundException` if downstream code implicitly needs them. Dependency drift in Hadoop can require updating exclusions.

Test signals: Build-level signal rather than unit tests; verifies intended classpath minimization when Maven resolves the module.
