# sources/sync-backup/rsync/daemon-parm.awk

## Purpose
Generates `daemon-parm.h` from `daemon-parm.txt`, turning declarative daemon parameter definitions into C structs, default values, parameter-table entries, and accessor macros/functions.

## Important APIs, Types, and Functions
The AWK script recognizes `Globals:` and `Locals:` sections and parameter lines beginning with `STRING`, `CHAR`, `PATH`, `INTEGER`, `ENUM`, `OCTAL`, `BOOL`, `BOOLREV`, or `BOOL3`. It emits `global_vars`, `local_vars`, `all_vars`, `Defaults`, `Vars`, `parm_table`, and `FN_*` accessor declarations into `daemon-parm.h`.

## Control Flow
The `BEGIN` block initializes generated-code fragments. Section rules enforce that globals come first and locals follow. Parameter rules normalize public names, strip dashes from C field names, choose C value/accessor types, append struct fields, default initializers, parameter metadata rows, and expanded-string tracking fields for string/path values. The `END` block writes the complete generated header or exits with failure.

## State and Persistence Behavior
Writes `daemon-parm.h` in the current working directory. The generated file is source state for daemon config parsing and accessors but is marked do-not-edit.

## Dependencies and Integration Points
Depends on AWK and the schema in `daemon-parm.txt`. Integrates with daemon configuration code that expects `parm_table`, `Defaults`, `Vars`, and `lp_*` accessors used heavily by `clientserver.c`.

## Risks and Test Signals
Risks are schema drift, malformed section ordering, invalid default C literals, duplicate/ambiguous names after dash stripping, and writing to the wrong current directory. Test signals include regenerating `daemon-parm.h`, compiling all `lp_*` references, and intentionally malformed `daemon-parm.txt` lines producing clear failures.
