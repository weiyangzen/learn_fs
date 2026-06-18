<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gss_names.c -->
# sources/user-network-fs/nfs-utils/utils/gssd/gss_names.c

## Purpose
This file converts authenticated GSS client names into hostbased service-name buffers that can be passed back to the kernel with a successful context downcall.

## APIs And Control Flow
`get_krb5_hostbased_name` handles Kerberos principal display strings containing both `@` and `/`; it copies the service/instance portion before the realm and converts the last slash to `@`, producing a hostbased service form. `get_hostbased_client_name` calls `gss_display_name`, rejects very large names, supports Kerberos OIDs through `krb5oid`, and returns an allocated string. `get_hostbased_client_buffer` wraps that string as a `gss_buffer_t`, including a terminating NUL in the length.

## State, Dependencies, And Integration
No persistent state is kept. Dependencies are GSSAPI display-name APIs, nfsidmap/nfslib includes, `krb5oid`, and `printerr`. `gssd_proc.c` calls this after `gss_inquire_context` to include the acceptor/client name in kernel downcalls.

## Risks And Test Signals
Risks include parsing displayed names with `sscanf`, only supporting Kerberos, allocation length equal to source length without extra slack but relying on zeroed memory, and embedding a NUL in the returned buffer length. Test with normal `nfs/server@REALM`, malformed names, huge names, unknown mechanisms, and buffer release by caller.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gss_names.c -->
