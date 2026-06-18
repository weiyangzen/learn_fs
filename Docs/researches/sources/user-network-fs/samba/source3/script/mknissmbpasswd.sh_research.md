# sources/user-network-fs/samba/source3/script/mknissmbpasswd.sh

Purpose: imports `smbpasswd` rows from stdin into a NIS+ `smbpasswd` table.

Important APIs, types, and functions: uses shell `read`, `cut`, `nistbladm -a`, and `nisdefaults -d`.

Control flow: read rows until an empty line, skip comments, split colon-separated fields, and add a NIS+ entry with selected password/account fields.

State and persistence: writes records into the NIS+ table `smbpasswd.org_dir.$(nisdefaults -d)`.

Dependencies and integration: depends on NIS+ tooling and legacy smbpasswd format.

Risks: unquoted `echo $row` loses whitespace and glob-like content, empty lines terminate processing, and field extraction is repeated many times. Sensitive password hashes are passed on command lines.

Test signals: comments, blank lines, malformed rows, hashes containing unusual characters, and NIS+ command failures.
