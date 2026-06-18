<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/pom.xml

Purpose: Maven module descriptor for `ozone-filesystem-common`, a jar containing shared Ozone filesystem implementations and client adapters.

Important APIs and functions: Maven coordinates inherit from `hdds-hadoop-dependency-client` version `2.3.0-SNAPSHOT`, artifact id `ozone-filesystem-common`, packaging `jar`, UTF-8 source encoding, dependencies, and compiler plugin configuration.

Control flow: build-time only. Maven resolves dependency versions through the parent, compiles module sources, and disables annotation processing with `maven-compiler-plugin` `<proc>none</proc>`.

State and persistence behavior: no runtime persistence, but dependency selection controls the runtime ABI available to filesystem code. Dependencies include Guava, OpenTelemetry API, Jakarta annotations, Apache Commons, Hadoop common/HDFS client, HttpClient, Ozone client/common/HDDS modules, Ratis common, and SLF4J.

Dependencies and integration: integrates the filesystem common jar with Hadoop FS APIs and Ozone client/HDDS protocol layers. Risks include parent-managed dependency drift, Hadoop compatibility constraints, and annotation processing being disabled. Test/build signals are Maven compile and downstream module tests that depend on these classes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/pom.xml -->
