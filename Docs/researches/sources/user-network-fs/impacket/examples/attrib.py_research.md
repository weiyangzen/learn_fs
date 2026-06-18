# sources/user-network-fs/impacket/examples/attrib.py

## Purpose

`attrib.py` queries or modifies Windows file and directory attributes over SMB without relying on remote shell execution. It supports SMB1 and SMB2/3 query/set information paths and exposes common file attribute flags as CLI options.

## Important APIs, Types, and Functions

`FileAttributes` is a dataclass holding boolean flags for known MS-FSCC file attributes. `pack` converts booleans to a bitmask, `unpack` creates an instance from a bitmask, and `__repr__` renders a compact attribute string. `attrib_query(connection, tid, fid)` reads basic file info using SMB1 or SMB2 structures. `attrib_set(connection, tid, fid, attribs)` writes basic file info with times set to zero and attributes set from the dataclass. `main` parses CLI, authenticates, opens the target file/directory, and dispatches query or set.

## Control Flow

After logging and argument parsing, the script validates the subcommand, parses the target identity, prompts for a password if needed, handles hashes/AES/Kerberos, connects to SMB, logs in, connects to the requested share, opens the normalized path with either `FILE_READ_ATTRIBUTES` or `FILE_WRITE_ATTRIBUTES`, and then queries or sets attributes. Query prints the compact attribute string plus share/path. Set builds `FileAttributes` from CLI booleans, calls `setInfo`, prints the new attributes, and finally closes the file, tree, and connection.

## State and Persistence Behavior

Query mode is read-only. Set mode mutates remote file or directory metadata. It does not persist local state. The code tries to close the file, disconnect the tree, and close the SMB session in a nested finally after successful connection/open.

## Dependencies and Integration Points

It depends on Impacket SMB connection APIs, SMB1 info classes, SMB2 `FILE_BASIC_INFORMATION`, NetBIOS default port constants, and example target parsing. It integrates with Windows/Samba filesystem metadata exposed via SMB.

## Risks and Edge Cases

Set mode writes a full attribute mask from only specified flags; omitted flags are cleared rather than preserving existing attributes. `FILE_ATTRIBUTE_NORMAL` semantics are special and can conflict with other flags, but the script leaves validation to the server. Time fields are set to zero in set structures; depending on SMB semantics this may preserve or alter timestamps. If `options.action` is invalid the script logs an error but does not immediately exit before later branching. Some attributes are represented in constants but not exposed as CLI set flags.

## Test Signals

Unit tests should cover `FileAttributes.pack/unpack/repr`, SMB1 versus SMB2 query/set structure selection, and CLI set-mask behavior. Integration tests should run query and set against a temporary file and directory on an SMB server and verify that only intended attributes change.
