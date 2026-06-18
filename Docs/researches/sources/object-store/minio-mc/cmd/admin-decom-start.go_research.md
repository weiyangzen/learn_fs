<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-decom-start.go -->
# sources/object-store/minio-mc/cmd/admin-decom-start.go

## Purpose
Implements `mc admin decommission start`, starting decommissioning for a specified server pool.

## Important APIs, types, and functions
Defines `adminDecommissionStartCmd`, `checkAdminDecommissionStartSyntax`, `startDecomMessage` with `String`/`JSON`, and `mainAdminDecommissionStart`.

## Control flow
Requires exactly target and pool arguments, cleans the target alias, creates an admin client, calls `DecommissionPool`, and prints success for the pool.

## State and persistence behavior
No local persistence. It mutates server-side pool decommission state.

## Dependencies and integration points
Depends on madmin decommission API through the admin client, console coloring, colorjson, global context, and probe/fatal handling.

## Risks and test signals
Wrong pool argument can initiate disruptive data movement. Tests should cover syntax validation, API errors, JSON/text output, and alias cleaning.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-decom-start.go -->
