# sources/user-network-fs/samba/source3/lib/netapi/examples/common.h

## sources/user-network-fs/samba/source3/lib/netapi/examples/common.h

Purpose: Declares the shared popt callback table and file helpers used by libnetapi examples.

Important APIs/types/functions: Declares `popt_common_callback()`, `popt_common_netapi_examples[]`, and macros `POPT_COMMON_LIBNETAPI_EXAMPLES`. Also declares `netapi_read_file()`, `netapi_save_file()`, and `netapi_save_file_ucs2()`.

Control flow: Example `long_options[]` arrays include `POPT_COMMON_LIBNETAPI_EXAMPLES`, making credential/debug/Kerberos parsing consistent across samples.

State and persistence behavior: Header owns no state; implementation mutates libnetapi context and local files.

Dependencies and integration points: Depends on popt and is included by nearly every file under `netapi/examples`.

Risks: Macro inclusion hides callback side effects; command examples must call `libnetapi_init()` before parsing.

Test signals: Build failures catch signature drift; command smoke tests catch option-table wiring.
