# sources/storage-engines/foundationdb/contrib/TraceLogHelper/TraceLogUtil.cs

Purpose: helper algorithms over parsed trace events.

Important APIs/functions: `TraceLogUtil.IdentifyFailedTestPlans(IEnumerable<Event>)`.

Control flow: streams events, tracks `TestPlan` entries keyed by `TestUID + TraceFile`, removes them when a matching `Test` summary appears, handles `-2.txt` restart companion cleanup, yields normal events immediately, and at the end emits synthetic `Test` objects of type `FailedTestPlan` for plans that never summarized.

State and persistence: in-memory dictionary of pending plans; no external writes.

Dependencies and integration: relies on `Event`, `TestPlan`, and `Test` models. Useful for tooling that wants missing test summaries represented as events.

Risks and test signals: key concatenation can collide without separators; restart filename split is simplistic. Test with completed plans, missing plans, restart `-1/-2` pairs, and empty TestUID.
