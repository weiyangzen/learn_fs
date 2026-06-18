# sources/user-network-fs/nfs-utils/systemd/fsidd.service

Purpose: `fsidd.service` starts the reexport fsid daemon required by reexport-aware mountd/server configuration.

Important APIs and control flow: The unit starts after `local-fs.target`, before `nfs-mountd.service` and `nfs-server.service`, and executes `/usr/sbin/fsidd`. Its install section is `RequiredBy=nfs-mountd.service nfs-server.service`, making those services pull it in when enabled.

State, dependencies, and integration: Runtime state is the sqlite reexport DB and AF_UNIX socket managed by `fsidd`. The unit provides ordering for `reexport.c` clients that connect during export processing.

Risks and test signals: There is no explicit `Type`, restart policy, or dependency on the database directory. Tests should enable nfs-server/mountd and verify fsidd starts early, socket is available, and failure propagates to reexport users as expected.
