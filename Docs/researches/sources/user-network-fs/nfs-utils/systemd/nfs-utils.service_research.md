# sources/user-network-fs/nfs-utils/systemd/nfs-utils.service

Purpose: `nfs-utils.service` is a grouping/restart unit for NFS server and client daemons.

Important APIs and control flow: It is a oneshot service that runs `/bin/true` and remains active. Units declaring `PartOf=nfs-utils.service` restart when this service is restarted, making it a service-style replacement for a restartable target.

State, dependencies, and integration: It owns no daemon state. Integration is through systemd `PartOf` relationships from units such as rpc.statd, rpc.gssd, blkmapd, and others.

Risks and test signals: It should not be stopped in normal operation, and only units that declare `PartOf` participate. Tests should restart it and verify expected daemons restart while unrelated units do not.
