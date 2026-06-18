## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/pom.xml

Purpose: Maven module descriptor for `ozone-cli-shell`, the native Ozone shell command jar.

Important APIs and control flow: inherits from `hdds-hadoop-dependency-client`, sets artifact/version/packaging, and enables classpath generation. Dependencies include Jackson, Guava, picocli and picocli-shell-jline3, Hadoop common/HDFS client, Ozone client/common/interface modules, Ratis, JLine, SLF4J, metainf-services, runtime Ozone filesystem, and test hdds-config. Build plugins wire SpotBugs to the empty exclude file, configure annotation processors for metainf-services and picocli native-image config generation, and override enforcer import restrictions for selected annotations.

State and dependencies: build-time only. It controls generated service metadata, native-image metadata, runtime classpath, and static analysis behavior.

Risks and test signals: dependency scope mistakes can break CLI packaging or interactive shell runtime. Annotation-processor configuration is important because shell command metadata is consumed by tooling.
