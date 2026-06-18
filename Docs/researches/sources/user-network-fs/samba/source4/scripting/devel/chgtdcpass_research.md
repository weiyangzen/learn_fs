<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/chgtdcpass -->
# sources/user-network-fs/samba/source4/scripting/devel/chgtdcpass

Purpose: development utility to update the local DC machine account password in samdb and secrets.ldb.

Important APIs/types/functions: `find_provision_key_parameters`, `update_machine_account_password`, `get_paths`, `get_ldbs`, and grouped transactions.

Control flow: parses options, opens provision LDBs, derives provision names/SIDs/realm data, calls the helper that updates the machine account password, and commits.

State and persistence behavior: mutates samdb and secrets.ldb credentials for the DC machine account.

Dependencies and integration points: integrates with Samba upgrade helper password logic and local provision paths.

Risks: uncoordinated machine-password changes can break DC authentication or replication. No automatic rollback beyond LDB transaction failure exists.

Test signals: successful commit and working machine-account Kerberos/NetLogon authentication afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/chgtdcpass -->
