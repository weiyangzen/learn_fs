<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_sid_passdb.h -->
# sources/user-network-fs/samba/source3/lib/util_sid_passdb.h

## Purpose
This header declares passdb SID responsibility predicates.

## Important APIs, types, and functions
It exposes `sid_check_object_is_for_passdb` and `sid_check_is_for_passdb`.

## Control flow
Callers use the object-only predicate for concrete account/group SID ownership and the broader predicate when domain SIDs are also valid inputs.

## State and persistence behavior
The header has no state. Implementation reads passdb responsibility configuration.

## Dependencies and integration points
It gives idmap/passdb consumers a small API without pulling in the responsibility logic implementation.

## Risks and edge cases
Using the broader predicate where only object SIDs are expected can route domain SIDs into object-handling code.

## Test signals
Compile coverage plus family/responsibility matrix tests in `util_sid_passdb.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_sid_passdb.h -->
