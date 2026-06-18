# sources/user-network-fs/impacket/examples/karmaSMB.py

## Purpose

`karmaSMB.py` runs a deceptive SMB server that responds to any requested share/path with configured file contents. It can serve a default file for all reads or map file extensions to specific payload files. It hooks SMB1 and SMB2 server commands to make arbitrary requested filenames appear to exist while redirecting actual file opens to local payload paths.

## Important APIs, Types, and Functions

`KarmaSMBServer` subclasses `Thread`. Its constructor builds an in-memory SMB server config with IPC$, NETLOGON, and SYSVOL shares, optionally enables SMB2, unregisters dangerous write/delete commands, hooks SMB1 commands and TRANS2 calls, hooks SMB2 tree connect/create/query/read/close commands, and registers an SRVS named pipe.

Key hooks are `findFirst2()`, `smbComNtCreateAndX()`, `queryPathInformation()`, `smb2TreeConnect()`, `smb2Create()`, `smb2QueryDirectory()`, `smb2Read()`, `smb2Close()`, and `smbComTreeConnectAndX()`. `setDefaultFile()` and `setExtensionsConfig()` define the payload mapping.

## Control Flow

The server accepts all SMB tree connects by synthesizing connected-share entries. When a client queries or opens a file, the hook extracts the original requested path, chooses a target local file from the extension map or default, rewrites the request to the local target, and delegates to the original Impacket server handler. Directory search responses are rewritten so returned filenames match the client's requested basename. SMB2 query-directory responses are synthesized with file size and timestamps from the chosen target file. SMB2 close may return `STATUS_USER_SESSION_DELETED` after reads to force clients to refresh cached directory data.

## State and Persistence Behavior

Persistent local state is limited to reading payload/config files. The server does not intentionally write remote data, and it unregisters many SMB write/delete operations. Runtime state includes `defaultFile`, `extensions`, the Impacket server object, SRVS helper thread, and per-connection `MS15011` dictionaries tracking requested file data, find state, and connection-stop behavior.

## Dependencies and Integration Points

It depends on Impacket `smbserver`, SMB1/SMB2 structures, NT status codes, SRVS server support, `ConfigParser`, and local filesystem metadata through `os.stat()`. It binds to `0.0.0.0:445`, so it requires privileges or capabilities on most systems and conflicts with any local SMB service.

## Risks and Edge Cases

The header warns that SMB2 behavior is cache-sensitive when clients request multiple filenames quickly. Write blocking is incomplete by design; only selected commands and access masks are denied. Config parsing assumes each non-comment line contains exactly one `=`. Missing payload files surface later during stat/open handling. The server claims all shares exist, which can surprise clients and logs. Binding to privileged port 445 and serving arbitrary configured files creates operational risk if run on a shared host.

## Test Signals

Tests should exercise extension mapping, default-file fallback, SMB1 open/search rewriting, SMB2 create/query-directory/read/close state transitions, and denied write/delete dispositions. Integration tests should run against Windows and Samba clients for SMB1 and SMB2, verify requested filenames appear while payload bytes match configured files, and ensure write attempts do not modify payload files.
