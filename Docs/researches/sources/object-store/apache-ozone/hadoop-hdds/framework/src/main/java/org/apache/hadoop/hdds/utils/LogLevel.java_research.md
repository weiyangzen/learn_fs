# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/LogLevel.java

## Purpose
`LogLevel` implements Hadoop-compatible runtime log-level inspection and mutation over HTTP/HTTPS. It contains a CLI that sends authenticated requests to `/logLevel` and a servlet that renders a small admin UI and applies log4j level changes.

## Important APIs and Types
The top-level `main` delegates to `CLI`, an internal `Tool`. `CLI.parseArguments` supports `-getlevel`, `-setlevel`, and `-protocol`. `CLI.connect` uses `AuthenticatedURL` with `KerberosAuthenticator` and optional `SSLFactory`. `Servlet.doGet` checks `HttpServer2.hasAdministratorAccess`, reads `log` and `level` parameters, and calls `process(Logger, level, out)`.

## Control Flow and State
The CLI validates a single operation, builds an HTTP(S) URL, connects, and prints only servlet output lines beginning with the marker `<!-- OUTPUT -->` after stripping HTML tags. The servlet displays submitted class/logger details, checks whether the SLF4J logger is backed by reload4j/log4j, validates the requested level using `Level.toLevel`, sets it when valid, and prints the effective level.

## Persistence, Dependencies, and Integration
State is runtime-only: log levels are changed in the active JVM logger hierarchy. Dependencies include Hadoop `ToolRunner`, servlet utilities, SPNEGO authentication, SSL client config, `HttpServer2` admin access, SLF4J, and log4j/reload4j classes.

## Risks and Test Signals
The servlet is operationally sensitive because it mutates logging dynamically; admin access enforcement is the key guard. Query parameters are concatenated directly by the CLI and should be tested for class names/levels requiring encoding. `IS_LOG4J_LOGGER` permanently disables adapter lookup after class-not-found. Tests should cover argument parser edge cases, protocol validation, HTTPS SSL setup, admin denial, invalid levels, non-log4j logger behavior, and marker parsing.
