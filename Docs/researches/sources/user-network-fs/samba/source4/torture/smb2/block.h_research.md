# sources/user-network-fs/samba/source4/torture/smb2/block.h

Purpose: This header declares SMB2 torture helper functions for blocking and unblocking transports and their backing TCP output paths. It is the small public contract implemented by `block.c`.

Important APIs and types: It declares `torture_get_local_port_from_transport(struct smb2_transport *)`, direct TCP helpers `torture_block_tcp_output_port()` and `torture_unblock_tcp_output_port()`, global iptables setup/cleanup helpers `torture_block_tcp_output_setup()` and `torture_unblock_tcp_output_cleanup()`, test lifecycle helpers `test_setup_blocked_transports()` and `test_cleanup_blocked_transports()`, and the lower-level `_test_block_smb2_transport()` / `_test_unblock_smb2_transport()` functions. Convenience macros `test_block_smb2_transport(_tctx, _t)` and `test_unblock_smb2_transport(_tctx, _t)` pass the expression name as the diagnostic transport name.

Control flow: Consumers call setup before tests that may use iptables, block one or more `struct smb2_transport` values during the scenario, unblock them if needed, and call cleanup afterward. The macros preserve a readable name without each caller manually passing a string.

State and persistence behavior: The header has no storage of its own. It exposes functions that can mutate host firewall state, SMB2 transport callback state, and global lease/oplock break tracking in the implementation.

Dependencies and integration points: This header assumes the including translation unit already sees Samba torture and SMB2 type declarations for `struct torture_context` and `struct smb2_transport`. It is used by SMB2 torture tests that need controlled transport failure or unacknowledged break behavior.

Risks: The macros stringify the transport expression, so complex expressions can produce long or awkward chain names in iptables mode. There is no include guard in this file; it relies on local include discipline. The API does not expose an error object, only boolean success/failure, so callers must rely on torture comments and assertions for diagnostics.

Test signals: Compile success in consumers validates visible type declarations. Runtime signals come from `block.c`: setup/block/unblock returning true, expected transport failure behavior, and cleanup restoring firewall state.
