# File Research: sources/virtualization/spdk/lib/iscsi/Makefile

This Makefile builds the SPDK `iscsi` library. It includes the library directory in `CFLAGS`, compiles connection, initiator group, core iSCSI, parameter, portal group, target node, subsystem, RPC, and task source files, and links against OpenSSL crypto via `LOCAL_SYS_LIBS = -lcrypto`.

It sets shared-object version `10.0`, names the library `iscsi`, uses `spdk_iscsi.map` for symbol exports, and includes the common SPDK library make rules.

Research notes: this group only includes the build file, not the listed iSCSI implementation sources. The Makefile shows that iSCSI depends on crypto and is split across transport/session/config/RPC/task modules.
