## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/test/java/org/apache/hadoop/ozone/repair/TestOzoneRepair.java

Purpose: command-level tests for the global Ozone repair CLI metadata and operator confirmation behavior.

Important APIs and control flow: `subcommandsSupportDryRun` recursively walks `new OzoneRepair().getCmd()` and asserts every leaf command contains `--dry-run` unless its user object implements `ReadOnlyCommand`. Other tests capture stdout/stderr, set `user.name` to `ozone`, feed stdin, and verify that risky executable commands prompt with the current user, abort on decline, proceed on "y", and skip prompts for parent/help/incomplete command invocations.

State and dependencies: mutates JVM global streams, stdin, and `user.name` during tests, restoring them in `@AfterEach`. Depends on picocli command metadata and the repair CLI prompt policy.

Risks and test signals: strong guard against adding destructive repair commands without dry-run support. It does not validate the underlying repair behavior beyond prompt flow.
