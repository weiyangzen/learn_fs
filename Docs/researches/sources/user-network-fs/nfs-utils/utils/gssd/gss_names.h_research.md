<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gss_names.h -->
# sources/user-network-fs/nfs-utils/utils/gssd/gss_names.h

## Purpose
This header declares the GSS-name conversion helpers used by gssd downcall processing.

## APIs And Types
It exports `get_hostbased_client_name`, which returns an allocated hostbased string, and `get_hostbased_client_buffer`, which returns the same data in a `gss_buffer_t` shape suitable for kernel downcall serialization.

## State, Dependencies, And Integration
There is no local state. The declarations require GSS types to be available from including translation units. The functions integrate `gss_names.c` with `gssd_proc.c` and server-side GSS code that needs normalized hostbased identities.

## Risks And Test Signals
Risks include no include guard, implicit dependency on prior GSS headers, and caller responsibility for freeing returned buffer values. Test by compiling all users with strict warnings and exercising successful and failed name conversion paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gss_names.h -->
