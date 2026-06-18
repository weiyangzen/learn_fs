# sources/user-network-fs/samba/source3/script/mknissmbpwdtbl.sh

Purpose: creates the NIS+ `smbpasswd` table and related group/access setup.

Important APIs, types, and functions: calls `nistbladm -D ... -c -s : smbpasswd_tbl`, `nisgrpadm -c`, `nischgrp`, and `nisdefaults -d`.

Control flow: one table creation command defines columns and access rights, then creates a NIS+ group and changes table group ownership.

State and persistence: mutates NIS+ namespace schema and group ownership.

Dependencies and integration: legacy NIS+ admin tools and Samba smbpasswd table schema.

Risks: no error handling between commands; partial setup can remain after failure. It embeds sensitive column access policy and assumes NIS+ is available.

Test signals: run in isolated NIS+ test domain, verify table schema, access rights, group creation, and partial-failure behavior.
