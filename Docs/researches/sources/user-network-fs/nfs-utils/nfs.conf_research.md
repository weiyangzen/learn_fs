# sources/user-network-fs/nfs-utils/nfs.conf

Purpose: `nfs.conf` is the default/general configuration template for NFS daemons and tools. It documents configurable sections and default values, with most settings commented out.

Important sections: `[general]`, `[nfsrahead]`, `[exports]`, `[exportfs]`, `[gssd]`, `[lockd]`, `[exportd]`, `[mountd]`, `[nfsdcld]`, `[nfsd]`, `[statd]`, `[sm-notify]`, and `[svcgssd]`. Active defaults in this file include `rdma=y` and `rdma-port=20049` under `[nfsd]`; most other settings are examples/comments.

Control flow: the file is read by nfs-utils components that use the configured `NFS_CONFFILE`. Daemon-specific parsers consume their sections to override compiled defaults and command-line values.

State and persistence: this is persistent system configuration, normally installed under `/etc/nfs.conf` or the configured `--with-nfsconfig` path.

Dependencies and integration points: integrates with `configure.ac` path substitution and daemons such as gssd, mountd, exportd, nfsd, statd, and sm-notify.

Risks: because `rdma=y` is uncommented, systems without RDMA support may see different behavior than a purely commented template would imply. Comments can drift from actual daemon defaults. Sensitive options such as keytab and credential cache paths need secure deployment choices.

Test signals: install and run `nfsconf`/daemon startup tests to verify each section is parsed, active RDMA defaults are honored or safely ignored, and commented options remain inert.
