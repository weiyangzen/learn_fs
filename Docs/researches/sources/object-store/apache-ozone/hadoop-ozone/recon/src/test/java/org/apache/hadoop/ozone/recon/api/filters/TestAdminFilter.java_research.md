# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/filters/TestAdminFilter.java

## Purpose
Tests Recon admin access policy. It verifies that REST endpoint classes are annotated with `@AdminOnly` unless explicitly allowlisted as non-admin, and that `ReconAdminFilter` permits or denies requests based on Ozone and Recon admin user/group configuration.

## Important APIs, Types, And Functions
The file covers `ReconAdminFilter.doFilter`, `AdminOnly`, `ReconServer.isAdmin`, `OzoneAdmins`, `OzoneConfiguration`, `OzoneConfigKeys`, `ReconConfigKeys`, `UserGroupInformation`, servlet `FilterChain`, `HttpServletRequest`, and `HttpServletResponse`. Reflection uses `Reflections`, `TypeAnnotationsScanner`, and `SubTypesScanner` to discover `@Path` endpoints.

## Control Flow
`testAdminOnlyEndpoints` scans `org.apache.hadoop.ozone.recon` for JAX-RS `@Path` classes, defines a non-admin allowlist, asserts those classes are not annotated, and asserts every other endpoint is annotated `@AdminOnly`. The remaining tests create configurations for Ozone admins, Recon admins, combined admins, no configured admins, starter-user auto-admin behavior, and starter user plus configured admins. `testAdminFilterWithPrincipal` mocks request principal, response, and filter chain, runs the filter, and verifies chain continuation or HTTP 403.

## State And Persistence
No persistent state is written. The only mutable process state is `UserGroupInformation.createUserForTesting` for group membership scenarios, reset in `finally` blocks. Mock `ReconServer` admin checks are implemented from config-derived `OzoneAdmins`.

## Dependencies And Integration Points
This test ties endpoint annotation policy to runtime authorization. It integrates Hadoop security configuration keys, Recon-specific admin config, servlet filter behavior, and package-level endpoint discovery. The allowlist includes cluster/node/status-style read-only endpoints such as `UtilizationEndpoint`, `ClusterStateEndpoint`, `NodeEndpoint`, `PipelineEndpoint`, `MetricsProxyEndpoint`, `ChatbotEndpoint`, and `TaskStatusService`.

## Risks
The reflection-based policy test can fail when a new endpoint is added without a deliberate admin decision, which is intentional. The allowlist must be kept small and reviewed because adding an endpoint there makes it public. Starter-user auto-admin behavior means an otherwise empty admin config still permits the Recon process user.

## Test Signals
Signals include non-admin endpoints being present and unannotated, all other endpoints requiring `@AdminOnly`, configured Ozone or Recon admin users passing, wildcard admins passing, configured admin groups passing, rejected users receiving 403, and the current user being accepted as starter admin.
