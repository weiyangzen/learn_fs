# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/userpasswd.c

Retrieves username/password credentials from factotum using `auth_getuserpasswd` with `proto=pass` and the supplied format string. It includes a compatibility fallback using nil key function for older factotum behavior.

Prints user and password on separate lines.
