# File Research: sources/os/bsd/netbsd-src/lib/libnpf/npf.h

Public `libnpf` API header. It defines opaque object types for configs, rules, rule procedures, tables, NAT entries, and extensions; iterator type `nl_iter_t`; the dynamic map ruleset prefix; extension callback typedefs; and connection callback type.

Important dependency: `<net/npf.h>` for kernel-facing NPF constants and structures.

The API covers config lifecycle/submission/import/export, ALG loading, parameters, dynamic rulesets, extension parameters, rule construction/querying/insertion/export, rule procedures, NAT construction/querying/insertion/lookup, connection listing, table creation/insertion/replacement, and private iteration/debug helpers under `_NPF_PRIVATE`.
