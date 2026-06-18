<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/SMB1FileStore.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/SMB1FileStore.cs

## Purpose
`SMB1FileStore` implements `ISMBFileStore` operations for a connected SMB1 tree.

## Important APIs and Types
Implemented operations include create, close, read, write, directory query via `TRANS2_FIND_FIRST2/NEXT2`, file information query/set, filesystem information query, security descriptor query, IOCTL/device control including pipe transceive, and tree disconnect. Max read/write sizes delegate to the owning client.

## Control Flow
Each method constructs the relevant SMB1 command or transaction subcommand, sends it with the tree ID, waits for the expected response command, parses success payloads, and returns the SMB status. Directory enumeration loops with find-next until end-of-search. Info-level passthrough controls whether native file information classes are used or converted to legacy query information levels. `FSCTL_PIPE_TRANSCEIVE` is routed to a named-pipe transaction; other IOCTLs use NT_TRANSACT IOCTL.

## State, Dependencies, and Integration
The file store keeps an `SMB1Client` reference and tree ID. It depends on many SMB1 command/transaction structures, query information helpers, security descriptor types, and NTSTATUS conventions. `NamedPipeHelper`, `ServerServiceHelper`, and DFS helpers call through this abstraction.

## Risks and Test Signals
Several inherited operations throw `NotImplementedException` (`FlushFileBuffers`, byte-range locks, handle-based directory query, filesystem set, change notify, cancel). `ToFileStatus()` mappings for create dispositions appear counterintuitive for open-if/overwrite cases. Tests should cover all implemented request/response pairs, timeout versus disconnect mapping, large directory enumeration, info-level fallback, pipe transceive, unsupported methods, and create-disposition status mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/SMB1FileStore.cs -->
