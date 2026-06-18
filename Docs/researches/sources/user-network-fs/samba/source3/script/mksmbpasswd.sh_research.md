# sources/user-network-fs/samba/source3/script/mksmbpasswd.sh

Purpose: AWK-based converter from passwd-style colon records to placeholder `smbpasswd` records.

Important APIs, types, and functions: sets `FS=":"`, prints a header, and emits `name:uid:XXXXXXXXXXXXXXXX...` records with disabled-password markers.

Control flow: for each input line, output one smbpasswd-format line using fields 1, 3, and 5.

State and persistence: writes to stdout only.

Dependencies and integration: depends on awk and input compatible with `/etc/passwd` field layout.

Risks: no filtering for system users or malformed records; output contains placeholder hashes and disabled account flags that need downstream handling.

Test signals: passwd fixtures with normal users, empty GECOS, malformed rows, and comments.
