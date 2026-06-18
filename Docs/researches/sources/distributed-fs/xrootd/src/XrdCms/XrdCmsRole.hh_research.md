# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRole.hh

Purpose: centralizes CMS role identifiers, display names, and compact type codes.

Important APIs/types: `RoleID` enumerates meta manager, manager, supervisor, server, proxy manager/supervisor/server, peer manager, peer, and noRole. `Convert()` maps config tokens to role ids. `Name()` returns human-readable names. `Type(RoleID)` returns compact codes such as `MM`, `M`, `R`, `S`, `PM`, `PR`, `PS`, `EM`, and `E`. `Type(const char *)` maps compact prefixes back to broad role categories.

Control flow: functions are static inline and table driven. `Convert()` supports one-token standard roles and two-token `proxy`/`meta` forms.

State and persistence: no mutable state; static const name arrays live in function scope.

Dependencies/integration: includes `<cstring>`. Used by protocol admission to label links and assign role IDs to nodes.

Risks: token matching is case-sensitive and exact. `Type(const char *)` maps any `P*` to `proxy` and any `E*` to `peer`, losing manager/server specificity. Comments require type strings to fit in four bytes including null.

Test signals: role token parsing matrix, name/type table bounds, and config parser tests for invalid roles.
