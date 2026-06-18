## sources/object-store/apache-ozone/hadoop-ozone/freon/pom.xml

Purpose: Maven build definition for the `ozone-freon` jar, Ozone's load generator and performance test CLI.

Important APIs/types/functions: declares dependencies on AWS S3 SDK, Jackson, Guava, commons-codec/io/lang3, picocli, metrics, OpenTelemetry, Hadoop common, HDDS/Ozone client/common/interface modules, Ratis, SLF4J, and metainf-services. Build plugins configure SpotBugs, compiler annotation processors, and an enforcer override for selected banned annotation imports.

Control flow: annotation processors generate `@MetaInfServices` service registrations for Freon subcommands and picocli GraalVM native-image metadata during compile. SpotBugs uses the empty exclude file. Enforcer allows this module to use the selected annotation processors while still banning Ozone config/request-validation annotations.

State and persistence behavior: build metadata only; generated service/native config artifacts are compile outputs.

Dependencies and integration points: Freon commands depend on Ozone client APIs, OM/SCM protocols, Hadoop FS, datanode container protocols, metrics, tracing, and picocli.

Risks: broad dependency surface can create classpath and shading conflicts; annotation processor configuration is required for subcommand discovery; runtime SLF4J reload4j dependency affects logging behavior.

Test signals: compilation should generate service entries for all `@MetaInfServices(FreonSubcommand.class)` commands; SpotBugs and enforcer should pass.
