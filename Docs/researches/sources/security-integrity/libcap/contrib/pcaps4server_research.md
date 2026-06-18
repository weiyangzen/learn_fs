<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/pcaps4server -->
# sources/security-integrity/libcap/contrib/pcaps4server

## Purpose
Legacy server-conversion script that changes selected daemons from root-owned operation to unprivileged users plus file capabilities.

## Important APIs, Types, And Functions
Defines message helpers, `checkReturnCode`, `p4r_test`, per-service convert/revert functions for apache2, samba, bind, dhcpd, and cupsd, plus usage dispatch.

## Control Flow
Requires root, then either converts all services or one selected service. Convert paths create service users/groups, edit config user/group entries, chown service directories and binaries, set setuid bits for service users, and apply `setcap`. Revert paths restore root ownership, remove setuid/filecaps, revert config snippets, and delete users/groups.

## State And Persistence Behavior
Highly persistent system mutation: user/group database, daemon config files, ownership of `/etc`, `/var`, and `/usr/sbin` paths, mode bits, and file capability xattrs.

## Dependencies And Integration Points
Assumes Slackware-like hard-coded paths, root privileges, `groupadd`, `useradd`, `chown`, `chmod`, `setcap`, `sed`, and installed daemons.

## Risks And Edge Cases
Dangerous on modern systems: hard-coded paths/users, typo `rev|renvert` in global revert dispatch, no backup of configs, and broad recursive chown. Should be treated as historical example code.

## Test Signals
Signals are command return codes checked after key mutations and visible capability/ownership changes on target daemons.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/pcaps4server -->
