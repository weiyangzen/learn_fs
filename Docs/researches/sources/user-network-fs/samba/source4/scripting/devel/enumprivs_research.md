<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/enumprivs -->
# sources/user-network-fs/samba/source4/scripting/devel/enumprivs

Purpose: small LSA RPC diagnostic that enumerates privileges on a server and prints display names.

Important APIs/types/functions: `get_display_name`, `lsa.lsarpc`, `OpenPolicy2`, `EnumPrivs`, `LookupPrivDisplayName`, and `security.SEC_FLAG_MAXIMUM_ALLOWED`.

Control flow: parses one server and credentials, refuses unauthenticated use, connects over `ncacn_np:<server>[print]`, opens an LSA policy handle, enumerates up to 100 privileges, looks up each display name, and prints LUID/name/display text.

State and persistence behavior: read-only RPC calls, no persistence.

Dependencies and integration points: Samba DCE/RPC LSA bindings and credential parser.

Risks: Python statement `''.decode('utf-8')` is invalid on Python 3 strings, so this historical script may require compatibility fixes. The 100 privilege cap is static.

Test signals: printed privilege rows with LUIDs and display strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/enumprivs -->
