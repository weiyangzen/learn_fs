<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/stunnel-rsyncd.conf.in -->
# sources/sync-backup/rsync/stunnel-rsyncd.conf.in

Purpose: template stunnel configuration for serving rsync daemon traffic over SSL/TLS on port 874. It launches rsync as an stunnel-executed daemon process after TLS termination.

Important APIs/types/functions: this is configuration, not code. Important directives are `foreground`, `pid`, listener/remote `TCP_NODELAY` socket options, `setuid`/`setgid`, `[rsync]`, `accept = 874`, certificate/key paths, client verification settings, `exec = @bindir@/rsync`, and `execargs = rsync --server --daemon .`.

Control flow: stunnel accepts a TLS connection, optionally verifies the client certificate depending on the selected `verify`/`CAfile` lines, and execs rsync in daemon-server mode. The comments show an alternate daemon config path using `--config=/etc/rsync-ssl/rsyncd.conf`.

State and persistence behavior: stunnel maintains a pid file at `/var/run/stunnel-rsyncd.pid`; rsync daemon state and logs are delegated to the daemon config. Certificate and key files are read from `/etc/rsync-ssl/certs`.

Dependencies and integration points: depends on stunnel, rsync installed at the configured bindir, server TLS material, system CA bundle or an allowed-client certificate bundle, and an rsync daemon configuration reachable by the executed server.

Risks: the default active example uses `verify = 0`, allowing any client to attempt a TLS connection; authentication then relies on rsync daemon configuration. Running stunnel as root is required for rsync chroot support but increases configuration sensitivity. Certificate/key paths are examples and must be protected on disk.

Test signals: validation is mostly operational: stunnel should parse the generated config, bind port 874, present the configured certificate, execute rsync, and allow `rsync://`-style daemon module access through TLS. A hardened deployment should test the commented `verify = 3` client-certificate mode.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/stunnel-rsyncd.conf.in -->
