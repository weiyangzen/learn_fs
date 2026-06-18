<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/gen_wsp_props.py -->
# sources/user-network-fs/samba/source4/scripting/bin/gen_wsp_props.py

## Purpose

`gen_wsp_props.py` generates C source tables describing Windows Search Protocol property sets from CSV input.

## Important APIs, Types, and Functions

`PropInfo` stores property metadata. Global maps `GuidToPropMap` and `GuidToPropMapLocation` group properties by GUID. Functions include `parseCSV()`, `parseGuid()`, `getBoolString()`, `getVtype()`, `generateSourceCode()`, and `main()`.

## Control Flow

The script expects a property CSV, output source path, and optional limited-info properties file. `parseCSV()` reads each non-comment line, splits up to ten columns, fills defaults, and appends properties by GUID. `generateSourceCode()` emits includes, per-GUID `full_propset_info` arrays, and a `full_propertyset` array mapping parsed GUID structs to property arrays.

## State and Persistence Behavior

Global maps accumulate parsed properties during one run. The output C file is persisted.

## Dependencies and Integration Points

Generated code includes Samba WSP NDR and utility headers. The script depends on Python `io` and expects CSV fields matching the documented property schema.

## Risks and Edge Cases

`parseCSV()` indexes `toParse[0]` without guarding empty lines. It uses simple comma splitting, so quoted commas are not supported. `parseGuid()` assumes brace-wrapped GUIDs. Dictionary iteration order controls output order on modern Python but was historically variable.

## Test Signals

Tests should cover full and limited-info CSV rows, blank/comment lines, every supported datatype mapping, vector properties, malformed GUIDs, and generated C compilation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/gen_wsp_props.py -->
