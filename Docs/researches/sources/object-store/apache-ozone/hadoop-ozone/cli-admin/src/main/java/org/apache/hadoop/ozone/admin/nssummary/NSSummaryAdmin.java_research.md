# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/nssummary/NSSummaryAdmin.java

## Purpose
Registers the `namespace` admin command group and computes the Recon web base URL used by namespace summary commands.

## Important APIs, Types, And Functions
`NSSummaryAdmin` implements `AdminSubcommand`, declares summary, du, quota, and dist subcommands, and exposes `getReconWebAddress`, `isHTTPSEnabled`, and `getOzoneConfig`. Helpers split host and port from config addresses.

## Control Flow
`getReconWebAddress` reads HTTP policy, chooses HTTP or HTTPS Recon address defaults, detects default wildcard host, and if default, replaces host with Recon RPC host while preserving web port. It returns `http(s)://host:port`.

## State And Persistence
No state is persisted. It reads Ozone configuration from the parent `OzoneAdmin`.

## Dependencies And Integration Points
Depends on Recon config keys, `HttpConfig`, `HttpServer2` scheme constants, `OzoneAdmin`, and service-loader registration.

## Risks And Test Signals
`getPort` assumes an address contains `:` and may not handle IPv6 bracket forms. Tests should cover HTTP and HTTPS policies, default host fallback, custom web host, RPC host fallback, and malformed config values.
