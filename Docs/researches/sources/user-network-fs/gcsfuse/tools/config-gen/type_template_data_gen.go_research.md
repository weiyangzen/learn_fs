<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/config-gen/type_template_data_gen.go -->
# sources/user-network-fs/gcsfuse/tools/config-gen/type_template_data_gen.go

Purpose: Builds template data for generated nested Go config structs from dotted config paths in params YAML.

Important APIs, types, and functions: `fieldInfo` describes generated struct fields. `typeTemplateData` groups fields under a generated type. `capitalizeIdentifier` validates and exports config path segments, `getGoDataType` maps params YAML types to Go types, `computeFields` expands a single config path into parent/child field entries, and `constructTypeTemplateData` merges/sorts/compacts fields across params.

Control flow: Each non-deprecated param config path is split on dots. Starting from `Config`, each segment becomes an exported field; non-leaf segments become nested type names like `MetadataCacheConfig`, while leaf segments use mapped data types. Fields are grouped by containing type, sorted by field name, compacted, then type groups are sorted by type name.

State and persistence behavior: Pure in-memory transformation with no I/O. Deprecated params with empty config path are skipped.

Dependencies and integration points: Used by `main.go` before template rendering. It must stay consistent with parser-supported types and flag template Go paths.

Risks and test signals: `cfgSegmentRegex` uses `MatchString` without anchors, so a partially matching invalid string could pass validation. `slices.Compact` only removes adjacent equal `fieldInfo`, so prior sorting by field name is important but may not deduplicate fields that differ in non-key metadata. Test coverage is indirect unless other generator tests exercise emitted structs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/config-gen/type_template_data_gen.go -->
