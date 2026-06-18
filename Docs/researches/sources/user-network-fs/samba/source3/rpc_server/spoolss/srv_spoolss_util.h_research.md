# sources/user-network-fs/samba/source3/rpc_server/spoolss/srv_spoolss_util.h

Purpose: Declares the spoolss-to-winreg utility interface implemented by `srv_spoolss_util.c`. It is the source3 spoolss server's typed contract for registry-backed printer and print driver operations.

Important APIs: The header declares `winreg_printer_binding_handle()` plus wrappers for printer lifecycle and metadata, printer data keys/values, driver list and driver info manipulation, printer security descriptors, forms, subkey enumeration, core printer drivers, and driver packages. It forward-declares `auth_session_info` and `dcerpc_binding_handle` and relies on generated spoolss/winreg types being visible to includers.

Control flow and state: No code or storage is defined here. All functions accept caller memory, session credentials, and `messaging_context`, making authentication and local RPC messaging explicit inputs. Persistent state is the Samba registry, reached indirectly by implementations.

Dependencies and integration: Used by spoolss RPC code that needs to read/write printer registry state through the internal winreg server. The API shape mirrors `cli_winreg_spoolss` operations and keeps server code from constructing winreg bindings manually.

Risks and test signals: Interface changes affect many spoolss operations. Watch for mismatches between pointer ownership, constness, and output allocation. Build tests plus spoolss functional tests around drivers, forms, printer data, and ACLs provide coverage.
