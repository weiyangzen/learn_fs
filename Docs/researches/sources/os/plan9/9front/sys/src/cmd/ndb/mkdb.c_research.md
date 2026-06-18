# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/mkdb.c

Converts merged legacy host database lines into ndb tuple format.

Key elements:
- Classifies fields as comments, sys names, Datakit names, IP addresses, or domain names.
- Accumulates related tuples until a new domain group starts, then prints an ndb entry.
- `tprint` emits `sys=`, `dom=`, `ip=`, and `dk=` attributes with continuation indentation.
- Adds `flavor=console` for specific Datakit console names under `nj/astro`.

Notable behavior:
- Domain duplicates suppress entry splitting.
- IP detection is simple dotted numeric syntax, not full IP parsing.
- Reads stdin and writes stdout through `Biobuf`.

Risks and quirks:
- Fixed arrays of 64 tuples and 64 fields can overflow if input lines are unusually large or grouped entries accumulate too many unique fields.
