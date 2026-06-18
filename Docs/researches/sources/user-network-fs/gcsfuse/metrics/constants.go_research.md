## sources/user-network-fs/gcsfuse/metrics/constants.go

Purpose: Defines numeric read-type constants and maps them to generated metric attribute values.

Important APIs/types/functions: `ReadTypeUnknown`, `ReadTypeSequential`, `ReadTypeRandom`, `ReadTypeParallel`, and `ReadTypeNames map[int64]ReadType`.

Control flow: static map lookup converts numeric classifier output into `ReadType` attributes.

State and persistence behavior: package-level map is mutable at runtime unless treated as constant by convention.

Dependencies and integration points: connects read classification code to generated metrics attributes from `metric_handle.go`.

Risks: map mutability could allow accidental test or runtime mutation. Numeric constants must stay aligned with read-classifier producers.

Test signals: no direct test here; metrics behavior tests using read types can catch mismatches.
