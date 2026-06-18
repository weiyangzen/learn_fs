# sources/storage-engines/foundationdb/contrib/TraceLogHelper/Event.cs

Purpose: shared C# data model for FoundationDB trace analysis in the Magnesium namespace.

Important APIs/types: `Severity`, `Event`, nested dynamic `MyExpando`, `TestPlan`, `Test`, graph structs/classes (`AreaGraphPoint`, `LineGraphPoint`, `Interval`, `MachineRole`, `Location`), `LocationTimeOp`, and `LocationTime`.

Control flow: `Event.DDetails` wraps dictionaries in `MyExpando` so details are accessible dynamically and as a dictionary. `FormatTestError` formats well-known event types using dynamic details and appends common error fields.

State and persistence: pure data objects; `original` optionally holds the parsed XML element for callers that need source data.

Dependencies and integration: used by `JsonParser`, `XmlParser`, and `TraceLogUtil`.

Risks and test signals: dynamic detail access throws at runtime if expected keys are absent; `emptyDetails` is static shared immutable-by-convention but the underlying dictionary is mutable. Tests should cover formatting for known error types and detail dictionaries.
