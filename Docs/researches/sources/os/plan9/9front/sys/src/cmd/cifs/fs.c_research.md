# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/fs.c

Generates textual contents for the CIFS synthetic info files exposed at the mounted root. It is not the 9P server itself; it supplies report functions registered by `info.c`.

`shareinfo`, `openfileinfo`, `sessioninfo`, `userinfo`, `groupinfo`, `domaininfo`, and `workstationinfo` query the remote server using Trans2 and RAP calls, then format the results into a `Fmt`.

`conninfo` prints current session identity, server name/domain/OS, clock slip, MTU, guest status, negotiated capabilities, security mode bits, and transport type.

`dfsrootinfo` recursively calls DFS referrals beginning at the domain root path `""` and prints DFS root/domain entries. `nodelist` backs domain/workstation browsing via server enumeration RAP calls.

Important dependencies: `T2fsdeviceinfo`, `T2fssizeinfo`, `RAPshareinfo`, `RAPsessionenum`, `RAPuserenum*`, `RAPgroup*`, `RAPServerenum*`, `RAPFileenum2`, `T2getdfsreferral`, and global `Sess`, `Ipc`, `Shares`.

Resource behavior: functions generally free per-entry strings after formatting, making these generators single-pass snapshots for `info.c` caching.
