## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/Shell.java

Purpose: abstract base for Ozone shell frontends, adding interactive/batch execution, tracing, deprecated option warnings, and user-friendly OM exception formatting to `GenericCli`.

Important APIs and control flow: constructor installs a custom execution strategy. `execute` warns on deprecated options, records command name, and if `--interactive` or `--execute` is present starts `REPL`; otherwise it initializes tracing and runs the parsed command under a tracing span. Batch mode wraps execution errors to exit the JVM with the CLI error code. `printError` unwraps `OMException` and prints concise result/message in non-verbose mode.

State and dependencies: holds command name and picocli spec for current execution. Depends on picocli, JLine factory, tracing utilities, and OM exception classes.

Risks and test signals: `System.exit` in batch errors is intentional but test-sensitive. Error formatting can hide stack traces unless verbose is enabled.
