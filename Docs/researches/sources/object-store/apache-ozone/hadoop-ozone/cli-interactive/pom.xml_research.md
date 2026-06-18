# sources/object-store/apache-ozone/hadoop-ozone/cli-interactive/pom.xml

Purpose: This Maven module defines `ozone-cli-interactive`, the top-level interactive CLI jar for Ozone.

Important APIs and types: It inherits from the root `ozone` parent, packages a jar, sets `classpath.skip=false`, and depends on picocli, `picocli-shell-jline3`, `ozone-cli-admin`, `ozone-cli-debug`, `ozone-cli-shell`, and runtime `slf4j-reload4j`.

Control flow and state: Build-time only. The dependencies assemble the command tree and REPL implementation used by `OzoneInteractiveShell`.

Dependencies and integration points: This module binds admin, debug, shell, tenant, and S3 command implementations into an interactive shell artifact.

Risks: Runtime behavior depends on transitive command registrations from the child CLI modules. Missing runtime logging or jline dependencies would break the shell startup.

Test signals: Build signals include dependency resolution, jar packaging, and execution of `OzoneInteractiveShell` with the expected command set.
