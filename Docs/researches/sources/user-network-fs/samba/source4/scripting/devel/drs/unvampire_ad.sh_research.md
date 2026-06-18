<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/drs/unvampire_ad.sh -->
# sources/user-network-fs/samba/source4/scripting/devel/drs/unvampire_ad.sh

Purpose: development cleanup helper that removes a vampired DC from a remote AD and deletes local private LDBs.

Important APIs/types/functions: sourced `vars`, `ldbdel -r`, remote LDAP URLs, administrator credentials, and `PREFIX/private/*.ldb` removal.

Control flow: sets default site if needed, deletes the machine from `CN=Computers`, `OU=Domain Controllers`, and the site server container on the remote server, then removes local `.ldb` files.

State and persistence behavior: deletes remote AD objects recursively and removes local provision database files.

Dependencies and integration points: coupled to the DRS development `vars` file and test AD topology.

Risks: destructive and credential-bearing. Wrong `server`, `machine`, `dn`, or `PREFIX` values can delete unintended objects or local databases.

Test signals: successful `ldbdel` commands and absent local `.ldb` files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/drs/unvampire_ad.sh -->
