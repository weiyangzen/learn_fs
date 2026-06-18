# sources/user-network-fs/nfs-utils/systemd/auth-rpcgss-module.service

Purpose: This unit loads the `auth_rpcgss` kernel module before GSS-related NFS services test kernel GSS proxy support.

Important APIs and control flow: It is a `DefaultDependencies=no` oneshot service ordered before `gssproxy.service`, `rpc-svcgssd.service`, and `rpc-gssd.service`, wants gssproxy and rpc.gssd, and runs `/sbin/modprobe -q auth_rpcgss`. It only runs when `/etc/krb5.keytab` exists and not inside a container.

State, dependencies, and integration: `RemainAfterExit=yes` leaves service state active after modprobe. It integrates with NFS client/server GSS units and kernel RPCSEC_GSS support.

Risks and test signals: Built-in kernel support makes modprobe fail harmlessly only if dependent units tolerate it. Keytab-based activation may skip environments using alternative credentials. Tests should verify ordering with gssproxy/rpc.gssd and behavior with module built-in, absent keytab, and containers.
