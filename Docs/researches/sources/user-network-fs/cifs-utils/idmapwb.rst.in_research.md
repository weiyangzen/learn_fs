<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/idmapwb.rst.in -->
# sources/user-network-fs/cifs-utils/idmapwb.rst.in

## Purpose

`idmapwb.rst.in` is the manual-page template for the winbind ID mapping plugin.

## Important APIs, Types, and Functions

It documents the plugin role, `@pluginpath@` symlink convention, winbind dependency, and related tools.

## Control Flow

Build substitution fills the configured plugin path, then `rst2man` generates `idmapwb.8`. Runtime flow is indirect: utilities load the plugin via the configured path.

## State and Persistence Behavior

The document describes dependency on winbind state and plugin symlink configuration.

## Dependencies and Integration Points

It integrates with `getcifsacl`, `setcifsacl`, `cifs.idmap`, Samba, `smb.conf`, and `winbindd`.

## Risks and Edge Cases

The page is concise and depends on other pages for operational details. It should keep the plugin path and winbind requirements explicit for packagers.

## Test Signals

Generated manpage checks should verify `@pluginpath@` substitution and related-tool references.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/idmapwb.rst.in -->
