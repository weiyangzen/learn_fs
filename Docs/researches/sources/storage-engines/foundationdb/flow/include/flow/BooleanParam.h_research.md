# sources/storage-engines/foundationdb/flow/include/flow/BooleanParam.h

Purpose: provides strong-ish typed boolean parameter wrappers to avoid ambiguous raw bool arguments.

Important APIs/types/functions: class `BooleanParam`; macros `FDB_DECLARE_BOOLEAN_PARAM`, `FDB_DEFINE_BOOLEAN_PARAM`, and `FDB_BOOLEAN_PARAM`.

Control flow: derived parameter classes wrap a bool and expose `True`/`False` static constants. Conversion to bool is constexpr.

State/persistence: each parameter object stores one bool. Static constants are inline definitions when macro-defined.

Dependencies/integration: used throughout Flow, including `FastInaccurateEstimate` and `IsSecureMem` in `Arena.h`.

Risks: implicit conversion back to bool means it prevents call-site ambiguity more than it enforces type safety internally. Macro use for nested classes requires correct fully qualified definitions.

Test signals: compile-time usability in APIs expecting named boolean params.
