# sources/security-integrity/selinux/libsemanage/src/port_record.c

Purpose: wraps libsepol network port record APIs for libsemanage and generic database use.

Important APIs/functions: compare/compare2/qsort, key create/extract/free, protocol get/set/string, low/high getters, single port and range setters, context get/set, create/clone/free, and `SEMANAGE_PORT_RTABLE`.

Control flow: all operations delegate to `sepol_port_*`. The qsort comparator is exported for local overlap validation. The record table is consumed by file and policydb database layers.

State/persistence: object state is held in libsepol port records. Persistence is through local file and policydb backends.

Risks: setters do not by themselves prevent overlapping ranges; local validation must run. Tests should cover protocol values tcp/udp/dccp/sctp, single and ranged ports, context assignment, key extraction, and sort ordering.
