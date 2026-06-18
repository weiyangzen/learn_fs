## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/OzoneShell.java

Purpose: main native Ozone shell command entry point, `ozone sh`/`sh`.

Important APIs and control flow: picocli `@Command` registers bucket, key, prefix, snapshot, tenant, token, and volume command groups, plus standard help and version provider. `main` instantiates `OzoneShell` and delegates to the inherited `run`.

State and dependencies: no direct persistence. Depends on the `Shell` base class for tracing, interactive mode, batch mode, and exception formatting.

Risks and test signals: subcommand list determines the public shell surface; missing entries remove command families. Tests for specific subcommands live elsewhere.
