<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/filters/ReconAdminFilter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/filters/ReconAdminFilter.java

## Purpose

`ReconAdminFilter` enforces admin-only access for servlet paths or resources protected by Recon's admin filter wiring.

## Important APIs and Types

It implements `javax.servlet.Filter`. `doFilter` extracts the request principal, creates a remote `UserGroupInformation`, checks authorization with `ReconServer.isAdmin`, and either continues the chain or returns HTTP 403.

## Control Flow

If authorization is disabled according to `OzoneSecurityUtil.isAuthorizationEnabled(conf)`, `hasPermission` returns true and all authenticated/principal-bearing requests are allowed. If a principal exists and is admin, the request proceeds. Otherwise the filter logs a rejection and sets status 403.

## State and Persistence

The filter holds injected `ReconServer` and `OzoneConfiguration`. It has no persistence.

## Dependencies and Integration Points

It integrates with servlet filter chains, Hadoop `UserGroupInformation`, Recon admin resolution, and Ozone security configuration.

## Risks and Edge Cases

When authorization is disabled but `userPrincipal` is null, the filter still rejects because the allow path is only entered inside `if (userPrincipal != null)`. It sets 403 but does not write an error body. It assumes upstream authentication has already populated a principal when needed.

## Test Signals

Tests should cover authz enabled admin/non-admin, authz disabled with and without principal, null principal rejection, status code, and filter-chain invocation count.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/filters/ReconAdminFilter.java -->
