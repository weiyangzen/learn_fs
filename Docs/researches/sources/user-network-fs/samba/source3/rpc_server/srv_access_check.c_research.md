# sources/user-network-fs/samba/source3/rpc_server/srv_access_check.c

Purpose: Shared RPC server access-control helpers. It wraps security descriptor checks with Samba privilege/root/system-token overrides and maps `MAXIMUM_ALLOWED_ACCESS` into concrete generic access requests.

Important APIs: `access_check_object()` calls `se_access_check()` against a supplied security descriptor and token, but can remove requested `rights_mask` bits before the descriptor check when either supplied privilege is present, later adding those bits back to granted access. It also overrides denial for system tokens with system privilege and for `root_mode()`. `map_max_allowed_access()` expands `MAXIMUM_ALLOWED_ACCESS` to read/execute for everyone and to generic all for root, Builtin Administrators, Builtin Account Operators, and Domain Admins on a DC.

Control flow and state: The functions are stateless except for reading process/root state, global SIDs, machine SID, and DC role. `access_check_object()` mutates `des_access` locally and writes `acc_granted`; `map_max_allowed_access()` mutates the caller's access mask in place.

Dependencies and integration: Depends on `../libcli/security/security.h`, privilege APIs, root/euid helpers, and passdb machine SID helpers. It is intended for SAMR/other RPC object access paths that need privilege-specific rights augmentation.

Risks and test signals: Privilege overrides can overgrant if callers pass an excessive `rights_mask`; the final code ORs the full mask, not only saved requested bits, despite the comment referencing saved bits. Test with normal users, root, system token, Builtin Administrators, Account Operators, Domain Admins, and requests with/without `MAXIMUM_ALLOWED_ACCESS`.
