# sources/security-integrity/selinux/libsemanage/src/ibendport_record.c

Purpose: wraps libsepol InfiniBand end-port record APIs in libsemanage names and record-table form.

Important APIs/functions: compare/compare2/qsort wrappers, key create/extract/free, ib device name get/set, port get/set, context get/set, create/clone/free, and `SEMANAGE_IBENDPORT_RTABLE`.

Control flow: every object operation delegates to the corresponding `sepol_ibendport_*` function, passing `handle->sepolh` where libsepol needs allocation/error context. The record table lets generic database code clone, compare, key, and free records without knowing ibendport internals.

State/persistence: the file owns no state beyond returned heap objects from libsepol. Persistence is provided by ibendport file and policydb backends. Dependencies include `sepol/ibendport_record.h`, `sepol/context_record.h`, `handle.h`, and `database.h`.

Risks: comments mention Pkey despite representing end ports, which can mislead maintainers. Validity checks for duplicate port entries happen in local validation, not setters. Tests should cover key construction, qsort ordering, device name allocation/free expectations, context set/get, and database CRUD using this record table.
