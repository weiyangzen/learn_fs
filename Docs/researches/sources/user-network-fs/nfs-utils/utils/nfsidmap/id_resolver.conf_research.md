## sources/user-network-fs/nfs-utils/utils/nfsidmap/id_resolver.conf

Purpose: Sample request-key rule connecting kernel id-resolver key requests to `/usr/sbin/nfsidmap`.

Important APIs/types/functions: The rule matches `create id_resolver * *` and invokes `nfsidmap -t 600 %k %d`, passing key serial and description with a 600 second timeout.

Control flow: The kernel key request mechanism calls this rule when NFS id mapping needs a userspace resolver.

State and persistence: Resolved values are instantiated in the keyring and expire according to the timeout.

Dependencies and integration: Requires Linux keyutils/request-key configuration and the installed `nfsidmap` binary path to match.

Risks and test signals: Wrong binary path or timeout prevents uid/gid/name resolution. Test with a mounted NFSv4 filesystem, `request-key`, and keyring inspection.
