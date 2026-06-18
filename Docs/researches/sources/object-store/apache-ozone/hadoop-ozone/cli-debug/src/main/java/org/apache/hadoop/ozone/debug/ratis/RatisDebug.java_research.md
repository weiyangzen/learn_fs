# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ratis/RatisDebug.java

Purpose: `RatisDebug` registers Ratis-related `ozone debug` commands.

Important APIs and types: It implements `DebugSubcommand`, is discovered through `@MetaInfServices`, and declares `RatisLogParser` as its subcommand.

Control flow and state: The class has no fields or methods beyond picocli metadata; picocli routes execution to the `parse` child command.

Dependencies and integration points: It integrates the Ratis parser into the generic `OzoneDebug` command tree.

Risks and test signals: Command registration is the main behavior to test. Functional parsing behavior lives in `RatisLogParser`.
