<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/rebuildextendeddn -->
# sources/user-network-fs/samba/source4/scripting/bin/rebuildextendeddn

## Purpose

`rebuildextendeddn` rewrites DN-valued and linked attributes in a Samba AD database to rebuild extended DN metadata.

## Important APIs, Types, and Functions

Functions include `message()`, `get_paths()`, and `rebuild_en_dn()`. It uses `ProvisionNames`, `provision_paths_from_lp()`, `get_linked_attributes()`, `get_dnsyntax_attributes()`, LDB transactions, and `search_options:1:2`.

## Control Flow

The script loads smb.conf and credentials with Kerberos disabled, resolves provision paths, opens `sam.ldb`, reads schema naming context, builds a list of linked and DN-syntax attributes, starts a transaction, searches all `cn=*` objects, replaces each relevant attribute with its current string values to force recalculation, verifies the attribute remains present with expected count, and commits.

## State and Persistence Behavior

It mutates `sam.ldb` inside one transaction by replacing attributes with equivalent values. It cancels the transaction on detected verification failure but may continue after printing errors in some branches.

## Dependencies and Integration Points

It depends on Samba provision/schema helpers, local LDB database paths, system session, and schema controls.

## Risks and Edge Cases

This is a broad database rewrite tool. It assumes `opts.quiet` exists even though no quiet option is added in this file, though `message()` is unused. Search filter `cn=*` may miss objects without CN. Failure handling prints diagnostics and cancels but does not immediately exit in the shown loop.

## Test Signals

Tests should run on disposable databases with known DN/link attributes, verify transaction rollback on mismatch, confirm extended DN metadata changes as expected, and check behavior with missing smb.conf or schema attributes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/rebuildextendeddn -->
