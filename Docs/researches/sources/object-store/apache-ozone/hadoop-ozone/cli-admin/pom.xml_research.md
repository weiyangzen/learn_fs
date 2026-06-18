# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/pom.xml

Purpose: This Maven descriptor builds the `ozone-cli-admin` jar, which contains admin subcommands and SCM/container operation client code for Ozone.

Important APIs and types: The module inherits from `hdds-hadoop-dependency-client`, sets artifact `ozone-cli-admin`, and enables classpath generation. Dependencies include Jackson, Guava, commons-io/lang3/codec, picocli, Hadoop common/HDFS client, HDDS CLI/client/common/config/interface/server framework modules, Ozone shell/client/common/interface modules, Ratis common, SLF4J, reload4j binding, and `metainf-services` as provided. Test dependencies include `hdds-common` test-jar and `hdds-test-utils`.

Control flow: The compiler plugin runs annotation processors for `@MetaInfServices` and picocli Graal native-image config generation, passing `-Aproject=group/artifact`. The enforcer plugin overrides root import restrictions for this module and bans selected HDDS config annotations.

State and persistence behavior: Build metadata only. It affects generated service-provider metadata and native-image configuration during compilation.

Dependencies and integration points: This module is an integration point between CLI command registration, picocli, SCM admin/client interfaces, Ozone shell/client libraries, and Hadoop dependencies.

Risks: Annotation processor configuration is critical for admin subcommands to be discoverable. Dependency changes can affect CLI packaging, native-image metadata, and runtime logging. The enforcer override must stay aligned with root policy.

Test signals: Maven compile, generated `META-INF/services` entries, picocli metadata generation, and downstream CLI tests resolving the admin commands.
