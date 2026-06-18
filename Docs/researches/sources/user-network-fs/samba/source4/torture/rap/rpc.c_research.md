# sources/user-network-fs/samba/source4/torture/rap/rpc.c

Purpose: This file checks consistency between RAP server information and the equivalent SRVSVC DCERPC server information.

Important APIs, types, and functions: `test_rpc_netservergetinfo()` opens an SRVSVC RPC pipe, calls `dcerpc_srvsvc_NetSrvGetInfo_r()` at level 101, then compares that with RAP `smbcli_rap_netservergetinfo()` at levels 0 and 1. `torture_rap_rpc()` registers the `rpc` sub-suite.

Control flow: The test obtains a DCERPC binding handle for `ndr_table_srvsvc`, queries `srvsvc_NetSrvGetInfo`, then queries RAP level 0 and level 1. It truncates the RPC server name to the 16-byte RAP name field and compares RAP name, major/minor versions, server type, and comment with RPC output. The pipe is freed at the end.

State and persistence behavior: This is read-only and maintains only transient RPC/RAP response state.

Dependencies and integration points: It depends on RAP client helpers, SRVSVC generated client stubs, `torture_rpc_connection()`, and the same SMB connection used by RAP tests. It is attached to the RAP suite from `rap.c`.

Risks: The comparison depends on RAP's legacy 16-character name semantics and on both RAP and RPC being backed by the same server identity. Differences in comment normalization, server type flags, or unavailable SRVSVC/RAP endpoints can fail the test.

Test signals: Passing results show that legacy RAP server info remains aligned with modern SRVSVC server metadata for the tested levels.
