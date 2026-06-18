## sources/security-integrity/audit-userspace/src/ausearch-common.h

Purpose: shared global search/report contract for `ausearch`, `aureport`, and parser modules.

Important APIs/types: declares global criteria such as `start_time`, `end_time`, event id, uid/gid/pid/session/syscall/exit filters, node list, filename/host/terminal/exe/comm/uuid/vm filters, success/config filters, and `escape_mode`. Defines `MAX_EVENT_DELTA_SECS`, `failed_t`, `conf_act_t`, `success_t`, and `report_t`.

Control flow/state: option parsers set these globals; `ausearch-match.c`, `aureport-scan.c`, `ausearch-parse.c`, and output modules read them to decide which fields to parse, match, and render.

Dependencies/integration: includes `ausearch-string.h` for node lists and `auparse-defs.h` for escape modes. This is the central coupling point across the utility cluster.

Risks/test signals: global mutable state makes reentrant or library-style use unsafe. Some parser paths only extract fields when the corresponding global filter/report need is set, so tests must configure globals to exercise fields. Regression tests should isolate each process or reset all globals.
