# sources/user-network-fs/samba/source3/rpc_server/srv_access_check.h

Purpose: Header for shared RPC server access-check helpers in `srv_access_check.c`.

Important APIs: Declares `access_check_object()` for descriptor/token/privilege-based access decisions and `map_max_allowed_access()` for converting `MAXIMUM_ALLOWED_ACCESS` into usable requested access bits. The signatures expose Samba security descriptors, security tokens, UNIX tokens, privilege IDs, desired/granted access masks, and debug labels.

Control flow and state: No local state. Callers provide all descriptors/tokens and receive results by output pointer or in-place requested-access mutation.

Dependencies and integration: Used by RPC servers needing consistent Samba access semantics. It depends on Samba security type declarations available from surrounding includes.

Risks and test signals: Signature drift breaks all shared authorization call sites. Tests should compile dependent RPC modules and verify privilege-sensitive access paths that call these helpers.
