# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/misc.c

Contains shared `pic` geometry, attribute, position, and object-allocation utilities.

It maps direction tokens to internal direction, extracts object components like `.x`, `.y`, `.wid`, `.ht`, and `.rad`, formats `sprintf` expressions, and builds typed attributes consumed by object generators.

Position helpers create points, interpolate between points, offset/add/subtract positions, locate object corners/center/start/end, and resolve references to first/last objects or objects inside blocks.

`makenode` allocates variable-sized `obj` records, initializes type/count/mode/current position/text range, grows `objlist`, and appends the object. `extreme` updates picture bounds.

Block variable lookup retrieves named positions or variables from a block-local symbol table.
