# sources/user-network-fs/samba/source4/dsdb/schema/schema_inferiors.c

## Purpose
`schema_inferiors.c` computes constructed schema fields related to class hierarchy and possible child object classes, especially `possibleInferiors` and `systemPossibleInferiors`.

## Important APIs, Types, and Functions
The exported entry point is `schema_fill_constructed`. Internal helpers are `schema_supclasses`, `schema_subclasses`, `schema_posssuperiors`, `schema_subclasses_recurse`, `schema_subclasses_order_recurse`, `schema_create_subclasses`, and `schema_fill_possible_inferiors`.

## Control Flow and Behavior
The code first clears temporary caches on every class. `schema_create_subclasses` builds direct subclass lists from each class's `subClassOf`, recursively expands subclass lists, initializes `subClass_order`, and walks from `top` to assign hierarchy depth. For each class, `schema_fill_possible_inferiors` scans all classes and includes non-abstract/non-auxiliary candidates whose computed possible superiors contain the current class. System-only candidates are excluded from `possibleInferiors` but retained in `systemPossibleInferiors`.

## State and Persistence Behavior
The function mutates in-memory computed fields on `struct dsdb_class`: `possibleInferiors`, `systemPossibleInferiors`, `subClass_order`, and temporary `tmp.*` lists. Temporary lists are freed after construction, while computed inferiors remain on the class objects.

## Dependencies and Integration Points
It depends on schema query by LDAP display name and Samba string-list helpers. The file documents that it is a C implementation of the logic in `dsdb/samdb/ldb_modules/tests/possibleInferiors.py`, making that Python test a direct oracle.

## Risks and Edge Cases
Missing `subClassOf` targets or missing `top` abort construction. Recursion assumes the class graph has no problematic cycles except `top SUP top`, which is special-cased. Many list operations do not check every allocation result after appends, so memory pressure can degrade into partial or NULL lists. Computed order drives objectClass sorting elsewhere, so incorrect hierarchy depth can affect validation.

## Test Signals
`possibleInferiors.py` is the key behavioral test. Additional tests should cover `top SUP top`, missing superclass, missing top, abstract/auxiliary exclusion, systemOnly split behavior, inherited possible superiors, subclass order, and schema reload recomputation from a clean cache.
