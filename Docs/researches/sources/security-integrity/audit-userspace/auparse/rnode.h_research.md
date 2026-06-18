<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/rnode.h -->
# sources/security-integrity/audit-userspace/auparse/rnode.h

## Purpose
Defines parsed audit record nodes and their field-array structure.

## Important APIs, types, and functions
`NFIELDS` sets the initial field allocation. `nvnode` holds field name, raw value, interpreted value, and item index. `nvlist` stores a dynamic array plus cursor/count/size and record-buffer ownership markers. `rnode` stores raw record text, interpretation text, cwd, record type, machine/syscall/a0/a1 context, parsed field list, event item index, source location, and next pointer.

## Control flow
Parser code builds `rnode` linked lists for event records, populates `nvlist`, and later interpretation/normalization traverse fields and records through cursor APIs.

## State and persistence behavior
All state is in-memory per parsed event. `record` and `interp` strings are owned by the record lifecycle; `nvlist.record/end` track the parsed buffer for safe cleanup.

## Dependencies and integration points
Used by `nvlist`, `interpret`, expression evaluation, event-list code, and normalization.

## Risks and test signals
Risks include ownership confusion between `rnode.record`, `nvlist.record`, and field pointers, plus stale syscall context. Tests should parse records with many fields, multi-record events, interpreted fields, and source location metadata.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/rnode.h -->
