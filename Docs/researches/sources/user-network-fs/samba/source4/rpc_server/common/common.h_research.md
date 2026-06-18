# sources/user-network-fs/samba/source4/rpc_server/common/common.h

Purpose: `common.h` defines small shared declarations for Samba4 DCERPC server interface implementations.

Important APIs, types, and functions: It forward declares share, DCERPC, NDR packet, and auth session types; defines `struct dcerpc_server_info` with domain name and version fields; and includes generated/common RPC server prototypes through `rpc_server/common/proto.h`.

Control flow: The header has no executable flow. RPC server C files include it for shared prototypes and server info type declarations.

State and persistence behavior: `dcerpc_server_info` is a data carrier only. The header stores no state.

Dependencies and integration points: It is used by RPC server implementations such as BackupKey and depends on generated/common prototype headers.

Risks: Duplicate forward declaration of `struct dcesrv_context` is harmless but untidy. Changes to this header affect many RPC server build units.

Test signals: Compile coverage is the main signal. Runtime server info behavior should be tested wherever `dcerpc_server_info` is populated and returned by common RPC helpers.
