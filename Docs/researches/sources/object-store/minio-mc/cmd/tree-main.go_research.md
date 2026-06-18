<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/tree-main.go -->
# sources/object-store/minio-mc/cmd/tree-main.go

Purpose: implements `mc tree`, rendering buckets/objects in tree form or delegating JSON output to recursive `ls`.

Important APIs/types/functions: tree glyph constants, `treeMessage`, `treeFlags`, `treeCmd`, `parseTreeSyntax`, `doTree`, and `mainTree`.

Control flow: syntax parsing accepts multiple targets, validates depth (`-1` unlimited, positive limited), parses rewind time, and pre-validates each target with `url2Stat`. `mainTree` defaults to `.` when no target is given, sets colors, and either calls `doTree` for text mode or `doList` with recursive options for JSON mode. `doTree` normalizes trailing separators, lists one directory level with `ShowDir: DirFirst`, delays printing each previous item until it knows whether it is the last child, recursively descends into directories within depth, and formats branch prefixes.

State and persistence: read-only listing command; only recursion stack and previous item are transient state.

Dependencies and integration points: uses generic client list/stat APIs, alias expansion, rewind parsing, `doList`, `printMsg`, and console colors.

Risks and test signals: recursion can be expensive on deep trees, and prefix/branch formatting is path-separator sensitive. Tests should cover depth validation, default target, JSON delegation, files vs directories, Windows-style examples, rewind propagation, and branch rendering for last/non-last children.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/tree-main.go -->
