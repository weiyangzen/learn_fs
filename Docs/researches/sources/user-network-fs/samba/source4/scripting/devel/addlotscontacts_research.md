<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/addlotscontacts -->
# sources/user-network-fs/samba/source4/scripting/devel/addlotscontacts

Purpose: development/load helper that bulk-creates contact objects under `OU=Contacts` in the local provision.

Important APIs/types/functions: `get_paths`, `get_ldbs`, `find_provision_key_parameters`, LDB `Message`, `MessageElement`, and transaction helpers.

Control flow: parses an optional contact count defaulting to 10000, opens local provision DBs without Kerberos, creates `OU=Contacts` if missing, loops adding `CN=contactN` objects, prints progress every tenth chunk or 5000 items, and commits the grouped transaction.

State and persistence behavior: mutates samdb by adding an OU and many `contact` objects.

Dependencies and integration points: intended for local Samba AD performance or scale testing, using the configured private provision.

Risks: large default object count can bloat a development DB. No cleanup path is provided. `increment = num_contacts / 10` is floating-point on Python 3, so modulo checks are unusual but still compare to a numeric value.

Test signals: object count under `OU=Contacts`, progress prints, and grouped transaction commit.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/addlotscontacts -->
