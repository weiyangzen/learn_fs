# sources/user-network-fs/samba/source4/lib/registry/interface.c

`interface.c` is the public registry-context wrapper API. It defines the predefined key table and provides functions to look up predefined names/handles, open keys, enumerate subkeys and values, read key info, add/delete keys, set/get/delete values, flush keys, and get/set security descriptors. Each call validates obvious NULL inputs and dispatches to `struct registry_operations` in the active backend.

The control flow is direct delegation; this file is the stable boundary between callers and backends such as `local.c`. Persistence is backend-specific and can be local hive files, LDB hives, or remote registry implementations outside this subset. Integration points include absolute-path helpers declared elsewhere and predefined HKEY constants from generated winreg headers.

Risks include inconsistent fallback behavior: comments mention fallback for open but the implementation requires `open_key`; most missing backend hooks return `WERR_NOT_SUPPORTED`. The predefined lookup is case-insensitive by name. Tests should cover each public wrapper with NULL keys, unsupported backend hooks, predefined key lookup, and propagation of backend WERRORs.
