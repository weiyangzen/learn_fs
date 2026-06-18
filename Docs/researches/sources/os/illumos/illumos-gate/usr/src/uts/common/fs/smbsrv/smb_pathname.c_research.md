# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_pathname.c

## Purpose

`smb_pathname.c` implements SMB pathname normalization, reduction, lookup, stream parsing, validation, CATIA translation, DFS preprocessing, short-name unmangling, VSS snapshot lookup adjustment, and share-root confinement. It is the core adapter between Windows path semantics and illumos vnode/name lookup semantics.

## Main Interfaces

- `smb_is_executable()` marks `.EXE`, `.COM`, `.DLL`, and `.SYM` files as executable.
- `smb_pathname_reduce()` returns the directory node for the penultimate path component and the last component name.
- `smb_pathname()` walks a path component by component, handles symlinks, case-insensitive lookup, short-name unmangling, CATIA translation, reparse-point detection, and optional VSS mount replay.
- `smb_lookuppathvptovp()` performs a direct vnode-to-vnode lookup from a start vnode and root vnode.
- `smb_pathname_init()` parses a request path into directory path, filename, stream name, and stream type fields.
- `smb_pathname_validate()`, `smb_validate_dirname()`, `smb_validate_object_name()`, and `smb_validate_stream_name()` enforce SMB-visible name restrictions and set SMB error status.
- `smb_stream_parse_name()`, `smb_is_stream_name()`, and `smb_strname_restricted()` support named stream parsing and classification.

## Behavior And Data Flow

`smB_pathname_reduce()` converts backslashes to slashes, canonicalizes duplicate separators, handles DFS root paths when DFS operation flags are present, optionally extracts VSS GMT tokens, then either strips the last component or preserves it for VSS discovery. It uses `smb_pathname()` to resolve the parent path and then optionally remaps the resolved node to a snapshot node through `smb_vss_lookup_nodes()`. It also enforces mount traversal policy unless `SMB_TREE_TRAVERSE_MOUNTS` is enabled.

`smB_pathname()` allocates pathname buffers and walks `upn` one component at a time. Each component is translated from CATIA v5 to v4 if enabled, looked up with `lookuppnvp()` via `smb_pathname_lookup()`, and retried through `smb_unmangle()` if short names are supported and the input may be mangled. It treats filesystem reparse-point attributes as `EREMOTE`, resolves symlinks itself so SMB nodes can be created for each component, enforces `MAXSYMLINKS`, and creates/returns `smb_node_t` objects with the correct parent directory node.

`smB_pathname_init()` first preprocesses paths: blank paths become `\`, old dialect wildcard conversion is applied, `/` becomes `\`, duplicate separators collapse, trailing slashes are removed, `$EXTEND` is hidden as `.$EXTEND` at filesystem root, and admin share `C$` paths are lowercased. It then splits the path into `pn_pname`, `pn_fname`, `pn_sname`, and `pn_stype`, treating `::$DATA` as the unnamed stream and defaulting missing stream type to `:$DATA`.

Validation rejects leading `..`, wildcards in directory path components, `.` as a filename, colons in directory names, DOS device-style names like `COM1:`, and stream types outside `$CA`, `$DATA`, and `$INDEX_ALLOCATION`.

## Dependencies

This file depends on illumos `pathname_t` and `lookuppnvp`, SMB node lookup/reference management, `smb_fsops`, CATIA helpers, VSS helpers, DFS UNC parsing, access-based enumeration flags, short-name mangling/unmangling, request-specific memory, and SMB error-reporting helpers.

## Notable Invariants And Risks

- `smb_pathname_reduce()` returns `*dir_node` held on success and releases it on error.
- `smb_pathname()` returns `*ret_node` held and optionally `*dir_node` held.
- `lookuppnvp()` consumes holds on `dvp` and `rootvp`; `smb_pathname_lookup()` explicitly takes those holds first.
- CATIA v5-to-v4 translation that introduces `/` is rejected with `EILSEQ`.
- Reparse points are detected before symlink handling because they use `VLNK` but have different SMB semantics.
- VSS handling intentionally tries snapshot conversion even after some lookup errors so previous versions can survive live-tree renames.
- Path parsing and validation are security-sensitive because mistakes can cross share roots, expose hidden quota directories, mishandle streams, or turn Windows path syntax into unintended vnode lookups.
