<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/chgkrbtgtpass -->
# sources/user-network-fs/samba/source4/scripting/devel/chgkrbtgtpass

Purpose: development utility to regenerate/update the local `krbtgt` account password in a Samba provision.

Important APIs/types/functions: `get_paths`, `get_ldbs`, `system_session`, `update_krbtgt_account_password`, and credentials forced to `DONT_USE_KERBEROS`.

Control flow: parses Samba and credential options, opens local provision LDBs, starts transactions, calls `update_krbtgt_account_password`, and commits.

State and persistence behavior: mutates samdb secrets for the Kerberos ticket-granting account and commits the change transactionally.

Dependencies and integration points: uses Samba upgrade helper password update logic. It is useful during provision repair or testing Kerberos key rollover behavior.

Risks: changing `krbtgt` can invalidate Kerberos behavior if not replicated or coordinated. No confirmation or backup is built in.

Test signals: successful transaction commit and subsequent Kerberos authentication/key version behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/chgkrbtgtpass -->
