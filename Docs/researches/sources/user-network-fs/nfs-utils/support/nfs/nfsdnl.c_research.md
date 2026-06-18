# sources/user-network-fs/nfs-utils/support/nfs/nfsdnl.c

Purpose: helper for sending nfsd generic-netlink commands with a string attribute.

Important API: `int nfsd_nl_cmd_str(int cmd, int attr, const char *value)`.

Control flow: allocates a libnl socket, connects to generic netlink, sets buffer sizes, resolves `NFSD_FAMILY_NAME`, allocates and fills a generic-netlink message, appends the string attribute, sends it, installs error/finish/ack callbacks, then receives until the callback-controlled return value is no longer positive.

State and persistence: no module-global state. It sends commands to kernel nfsd netlink state and reports kernel/libnl errors.

Dependencies and integration: optional `CONFIG_NFSDCTL` build path. Depends on libnl3/genl, `nfsd_netlink.h` or system kernel header, `nfslib.h`, and `xlog.h`.

Risks: `nla_put_string()` return is not checked. The receive loop ignores the return value of `nl_recvmsgs()`, relying on callbacks to update `ret`. Buffer size is fixed at 4096. Return values are negative errno-style except success 0.

Test signals: missing family, allocation failures, kernel error ack, successful ack, invalid command/attribute, and string values near netlink message limits.
