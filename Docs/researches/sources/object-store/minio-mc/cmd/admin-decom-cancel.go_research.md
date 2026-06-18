<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-decom-cancel.go -->
# sources/object-store/minio-mc/cmd/admin-decom-cancel.go

## Purpose
Implements `mc admin decommission cancel`, cancelling a specific pool decommission or listing cancellable in-progress decommissions when no pool is supplied.

## Important APIs, types, and functions
Defines `adminDecommissionCancelCmd`, `checkAdminDecommissionCancelSyntax`, and `mainAdminDecommissionCancel`.

## Control flow
The command accepts target plus optional pool. With a pool, it calls `CancelDecommissionPool`. Without a pool, it calls `ListPoolsStatus`, filters started and incomplete decommissions, formats capacity/status rows, and displays a table.

## State and persistence behavior
Specific-pool mode mutates server decommission state. Listing mode is read-only. No local state is persisted.

## Dependencies and integration points
Depends on madmin pool status/decommission APIs, humanize formatting, console tables, color setup, and shared CLI/probe helpers.

## Risks and test signals
The table allocation uses filtered length but iterates original statuses with incremented indexes, which can be fragile if skipped rows create gaps. Tests should cover no active pools, mixed complete/incomplete pools, specific cancellation, and JSON expectations if added later.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-decom-cancel.go -->
