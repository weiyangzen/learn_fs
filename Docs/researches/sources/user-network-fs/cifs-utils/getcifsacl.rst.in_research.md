<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/getcifsacl.rst.in -->
# sources/user-network-fs/cifs-utils/getcifsacl.rst.in

## Purpose

`getcifsacl.rst.in` is the manual-page template for displaying CIFS/NTFS ACL security descriptors.

## Important APIs, Types, and Functions

It documents `getcifsacl [-v|-r]`, the `-R` recursive option, raw mode, plugin path substitution through `@pluginpath@`, output formatting expectations, and related tools.

## Control Flow

The build substitutes the plugin path and converts RST to `getcifsacl.1`. Runtime flow described is reading a file object's security descriptor and printing ACE fields separated by `/`.

## State and Persistence Behavior

The manpage describes read-only inspection of CIFS xattr-backed descriptors and plugin-based SID mapping.

## Dependencies and Integration Points

It integrates with `mount.cifs(8)`, `setcifsacl(1)`, CIFS kernel support, and idmap plugins.

## Risks and Edge Cases

The synopsis omits `-R` even though the options section documents it and the code supports it. Documentation should also remain aligned with SACL fallback behavior and raw output.

## Test Signals

Generated manpage checks should compare documented options with `getcifsacl.c` and verify `@pluginpath@` substitution.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/getcifsacl.rst.in -->
