<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/nvlist.h -->
# sources/security-integrity/audit-userspace/auparse/nvlist.h

## Purpose
Declares the internal name/value list API used for parsed audit record fields and interpretation lists.

## Important APIs, types, and functions
Inline helpers expose count, reset-to-first, current node/name/value/interpreted value access. Hidden functions create, clear, iterate, append, find, type-adjust, interpret, and move by index.

## Control flow
Parser code appends fields as it tokenizes a record, then callers move through fields or search by name. Interpreted values are requested lazily through the API.

## State and persistence behavior
The header operates on `nvlist` and `nvnode` definitions from `rnode.h`; state is stored inside records or parser interpretation lists.

## Dependencies and integration points
Depends on config, private auparse messaging, `rnode.h`, and event list definitions. It integrates parsing, interpretation, and normalization cursor operations.

## Risks and test signals
Risks are unsafe inline access when `cnt == 0` or `cur` is invalid. Tests should cover empty list accessors, cursor movement, and name lookup after partial iteration.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/nvlist.h -->
