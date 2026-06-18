# sources/user-network-fs/samba/source3/registry/reg_import.h

## Purpose
`reg_import.h` defines the callback contract used by `reg_import.c` to turn parsed `.reg` data into registry API operations.

## Important APIs, Types, And Functions
It declares callback typedefs for opening, closing, creating, deleting keys, deleting values, and setting values in three forms: raw blob, `struct registry_value`, or `struct regval_blob`. `struct reg_import_callback` groups these callbacks, a setter union, a `setval_type` enum (`NONE`, `BLOB`, `REGISTRY_VALUE`, `REGVAL_BLOB`), and opaque `data`. `reg_import_adapter()` creates the parser callback object.

## Control Flow
Import users populate `struct reg_import_callback`, choose a setter mode, create an adapter, and pass it to the `.reg` parser. The implementation supplies no-op defaults for non-value operations but requires the selected setter function for value import modes.

## State And Persistence
The header defines no state itself. Persistence is controlled entirely by callback implementations supplied by consumers.

## Dependencies And Integration Points
It includes `reg_parse.h` and forward-declares registry value/blob types. It is the public adapter boundary between parser code and registry mutation backends.

## Risks And Test Signals
Tests should compile each setter variant and validate callback signatures. Runtime tests should verify no-op defaults, selected setter assertions, and that callback private data is passed unchanged through all operations.
