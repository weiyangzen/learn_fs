<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gss_util.c -->
# sources/user-network-fs/nfs-utils/utils/gssd/gss_util.c

## Purpose
This file contains general GSSAPI support for gssd: status reporting, acceptor credential acquisition, mechanism availability checks, and global credential cleanup.

## APIs And Control Flow
`display_status_2` converts major and minor GSS status codes into readable diagnostics and treats expired credentials as lower-verbosity noise. `pgsserr` is the public wrapper. `gssd_acquire_cred` imports an optional hostbased server name, acquires acceptor credentials into global `gssd_creds`, reports detailed failures, and releases imported names. `gssd_check_mechs` verifies that the GSS library returns at least one supported mechanism. `gssd_cleanup` releases the global credential handle.

## State, Dependencies, And Integration
Global state is `gssd_creds` and `g_mechOid`. Dependencies include GSSAPI, optional Kerberos name types, error utilities, and gssd globals. Client upcall processing uses the status helpers; server-side code can acquire acceptor creds through this file.

## Risks And Test Signals
Risks include global credential lifetime, limited major-status name mapping, possible null release paths around target names, and diagnostic verbosity hiding important credential-expiry behavior. Test GSS library misconfiguration, no mechanisms, bad service names, expired credentials, and cleanup idempotence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gss_util.c -->
