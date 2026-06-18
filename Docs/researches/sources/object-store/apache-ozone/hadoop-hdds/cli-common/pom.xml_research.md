# sources/object-store/apache-ozone/hadoop-hdds/cli-common/pom.xml

Purpose: Maven module definition for shared Apache Ozone CLI infrastructure.

Important APIs/types/functions: The artifact is `hdds-cli-common`, packaging `jar`. It depends on picocli, Jakarta annotations, Hadoop common, `hdds-common`, Ratis common, and SLF4J. Build plugins configure SpotBugs, javac annotation processors, and an enforcer override.

Control flow: During compile, javac runs `org.kohsuke.metainf_services.AnnotationProcessorImpl` and picocli's GraalVM native image config generator. The default compile execution passes `-Aproject=${project.groupId}/${project.artifactId}`. Enforcer bans `Config` and `ConfigGroup` imports in this module while explaining the selected annotation processors.

State and persistence behavior: Produces the shared CLI jar and generated annotation/native-image metadata. No runtime state in the POM itself.

Dependencies and integration points: This module is consumed by Ozone admin/debug/repair CLI tools and any command package using `GenericCli`, marker interfaces, or picocli helpers.

Risks: The native-image and `MetaInfServices` processors are part of compile behavior; removing them can break dynamic command discovery or native packaging. The enforcer override is intentionally narrow and should be kept aligned with allowed processors.

Test signals: Maven compile, SpotBugs, service metadata generation, and CLI tests using dynamic subcommands are the main build signals.
