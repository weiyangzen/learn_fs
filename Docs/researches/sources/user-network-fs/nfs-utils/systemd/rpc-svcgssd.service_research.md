# sources/user-network-fs/nfs-utils/systemd/rpc-svcgssd.service

Purpose: This unit runs the legacy server-side RPCSEC_GSS daemon when gssproxy support is unavailable.

Important APIs and control flow: It starts after local filesystems and gssproxy, is `PartOf` both nfs-server and nfs-utils, and has OR-style `ConditionPathExists` checks requiring no gssproxy pid and no `/proc/net/rpc/use-gss-proxy`, plus a keytab. It runs `/usr/sbin/rpc.svcgssd` as a forking service.

State, dependencies, and integration: It integrates with Kerberos keytab state, gssproxy detection, and server GSS service startup.

Risks and test signals: Systemd `ConditionPathExists=|` semantics are subtle, so packaging changes can accidentally start both gssproxy and svcgssd or neither. Tests should cover gssproxy available/unavailable, missing keytab, restart via server/nfs-utils, and kernel support detection.
