# sources/object-store/apache-ozone/hadoop-ozone/cli-interactive/src/main/java/org/apache/hadoop/ozone/shell/OzoneInteractiveShell.java

Purpose: `OzoneInteractiveShell` starts a JLine/picocli REPL that groups all major Ozone command families under one interactive `ozone` prompt.

Important APIs and types: It uses `PicocliCommandsFactory`, `CommandLine`, `REPL`, `Shell`, `OzoneShell`, `TenantShell`, `S3Shell`, `OzoneAdmin`, `OzoneDebug`, `OzoneInteractiveWelcome`, and a private `TopCommand`.

Control flow: `main` creates a picocli factory and top command, adds subcommands `sh`, `tenant`, `s3`, `admin`, and `debug`, creates a lightweight `Shell` implementation for name/prompt/welcome lines, and constructs a `REPL`. The top command itself is a no-op grouping command.

State and persistence behavior: There is no persistence. Runtime state is the REPL session, command tree, and welcome-line list.

Dependencies and integration points: It is the executable entry point for the `ozone-cli-interactive` module and composes command sets from separate Ozone CLI artifacts.

Risks: The `new REPL(...)` constructor is expected to start or own the interactive loop; if it does not, `main` would exit immediately. Command aliases and option behavior depend on the embedded child command instances. There is no direct handling of startup exceptions.

Test signals: Tests should verify subcommand registration, prompt/name values, welcome lines, and that basic commands can be invoked through the REPL command tree.
