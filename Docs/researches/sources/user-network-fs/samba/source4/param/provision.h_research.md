# sources/user-network-fs/samba/source4/param/provision.h

Purpose: `provision.h` declares C structures and entry points for Samba provisioning helpers.

Important APIs, types, and functions: It defines `struct provision_settings`, `struct provision_result`, `struct provision_store_self_join_settings`, and prototypes for `provision_bare`, `provision_store_self_join`, and `provision_get_schema`.

Control flow: The header is a contract only. Callers fill provision settings, call the C glue, and receive LDB/loadparm outputs or error strings.

State and persistence behavior: `provision_settings` carries target DNs, server identity, realm/domain, machine password, target directory, and `use_ntvfs`. `provision_result` returns domain DN, SAM database, and loadparm context. Self-join settings carry secrets database material including SID, password, secure channel type, and key version.

Dependencies and integration points: It references LDB, loadparm, tevent, domain SID, and Netlogon secure channel types. `provision.c` implements the declared calls using Samba Python.

Risks: Most fields are raw pointers with no ownership annotation, so caller lifetime must be clear. Missing or NULL settings propagate into Python calls and may fail late.

Test signals: Compile coverage plus integration tests for all three public calls are needed; boundary tests should omit optional DN fields and validate required field failures.
