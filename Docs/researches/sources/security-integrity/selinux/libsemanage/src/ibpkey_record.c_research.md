# sources/security-integrity/selinux/libsemanage/src/ibpkey_record.c

Purpose: wraps libsepol InfiniBand P_Key record APIs for libsemanage and exposes them through `record_table_t`.

Important APIs/functions: compare/compare2/qsort, key create/extract/free, subnet prefix string and byte getters/setters, low/high getters, pkey/range setters, context getters/setters, create/clone/free, and `SEMANAGE_IBPKEY_RTABLE`.

Control flow: the implementation delegates directly to `sepol_ibpkey_*` with `handle->sepolh` when needed. The qsort comparator dereferences record pointers and uses libsepol ordering, which local validation relies on to detect neighboring overlaps.

State/persistence: object memory is owned by libsepol allocation routines. Persistence is through the file and policydb backends. Risks include callers setting invalid ranges; overlap semantics are enforced later in local validation. Test signals include single pkey and range setup, subnet prefix string/byte conversion, context assignment, and record table CRUD.
