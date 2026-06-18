# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ClientBooleanParams.h

Purpose: central declaration of strongly typed boolean parameters used by client APIs.

Important APIs and types: expands `FDB_BOOLEAN_PARAM` for `EnableLocalityLoadBalance`, `LockAware`, `Reverse`, `Snapshot`, `IsInternal`, `AddConflictRange`, `UseMetrics`, and `IsSwitchable`. Each macro creates a named boolean wrapper type used to avoid ambiguous raw `bool` parameters.

State and persistence: no runtime state and no persistence. The types affect API signatures and call-site clarity.

Dependencies and integration: includes `flow/BooleanParam.h`; these parameter types appear across NativeAPI, transaction, read, conflict, metrics, and switchable database/client interfaces.

Risks: adding or renaming a param changes public/internal API source compatibility. Because these are header-level type declarations, include order and duplicate definitions must remain guarded by `#pragma once`.

Test signals: compile-time use is the primary validation; behavior is covered by callers that branch on these parameter values.
