# sources/security-integrity/selinux/libsemanage/src/ibendports_local.c

Purpose: exposes local InfiniBand end-port CRUD APIs and enforces no duplicate `(ibdev_name, port)` records.

Important APIs/functions: local modify/delete/query/exists/count/iterate/list wrappers and `semanage_ibendport_validate_local`.

Control flow: CRUD delegates to `semanage_ibendport_dbase_local(handle)`. Validation lists local records, sorts them with `semanage_ibendport_compare2_qsort`, then scans neighboring records with matching device names. If two records share the same port, it reports an `already exists` error.

State/persistence: local records are persisted through the local ibendport database. Validation allocates name strings from libsepol getters and frees all listed records before returning.

Risks: memory cleanup depends on freeing transient strings each loop; only same-device duplicates are checked. If compare order changes, the neighbor scan assumption could break. Tests should cover empty list, unique ports on same device, same port on different devices, duplicate same device/port, and error paths from getter failures.
