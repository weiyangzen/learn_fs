# sources/user-network-fs/samba/source3/script/creategroup

Purpose: example shell script for Samba's `add group command`, designed to create groups for difficult NT group names.

Important APIs, types, and functions: calls `/usr/sbin/groupadd`, `dd`, `md5sum`, `cut`, `expr`, `getent`, and `grep`.

Control flow: attempt to create the requested group name. On failure, generate a random `nt-xxxxx` group name and retry up to 10 times. Finally print the numeric GID for the created group.

State and persistence: mutates the local system group database through `groupadd`.

Dependencies and integration: depends on system account tools and `/dev/urandom`. Intended for Samba configuration hooks, not as a general safe utility.

Risks: needs privilege, assumes GNU-ish tools, uses grep with an unescaped group name prefix, and can create random local groups if the requested name is invalid or already exists.

Test signals: test normal creation, invalid NT-style names, already-existing groups, exhausted retries, and GID output.
