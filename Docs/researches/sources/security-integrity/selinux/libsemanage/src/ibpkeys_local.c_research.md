# sources/security-integrity/selinux/libsemanage/src/ibpkeys_local.c

Purpose: provides local InfiniBand P_Key CRUD APIs and validates that local ranges do not overlap for the same subnet prefix.

Important APIs/functions: local modify/delete/query/exists/count/iterate/list wrappers and `semanage_ibpkey_validate_local`.

Control flow: CRUD delegates to `semanage_ibpkey_dbase_local(handle)`. Validation lists and sorts local records, then for each record finds the next record with the same subnet prefix bytes. Because sort order is by subnet and lower bound, `low2 <= high` signals overlap.

State/persistence: local records persist in the local ibpkey database. Validation is read-only except for allocations during list/getter calls.

Risks: the function allocates subnet prefix strings but does not visibly initialize/free both string pointers in all loop paths, so leak/error-path tests are useful. Correctness depends on libsepol compare ordering. Tests should cover adjacent non-overlapping ranges, true overlap, different subnet prefixes, empty lists, and malformed local files.
