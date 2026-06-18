# sources/storage-engines/foundationdb/contrib/commit_debug.py

## Purpose
Converts FoundationDB `CommitDebug` trace XML events into Chrome tracing JSON duration spans, making commit pipeline latency phases visible in `chrome://tracing`.

## Important APIs, Types, And Functions
`locationToPhase` maps trace `Location` values to synthetic begin/end events such as `Commit`, `CommitVersion`, `Resolver.PipelineWait`, `Resolver.Conflicts`, `Proxy.Processing`, `TLog.PipelineWait`, and `TLog.FSync`. `CommitDebugHandler` is an SAX handler that emits JSON trace events. `do_file()` parses plain or gzip XML. `main()` accepts a trace file, `.xml.gz`, or directory of gzipped traces.

## Control Flow
For each `Event` element of type `CommitDebug`, the handler establishes a relative start time, derives `pid`/`tid` from `Machine`, and either records a begin timestamp or emits a complete duration event when a matching end location is encountered. Directory input is merged chronologically into `combined.xml.gz` before parsing.

## State And Persistence
Writes the output trace JSON file. For directory input it may create and reuse `combined.xml.gz`. In-memory `_data` tracks active spans keyed by machine and synthetic span name.

## Dependencies And Integration
Uses Python stdlib `xml.sax`, `gzip`, `glob`, `heapq`, and JSON. Input format is FoundationDB trace XML with `CommitDebug` event locations matching `locationToPhase`.

## Risks
The output intentionally starts with `[ ` and leaves the closing bracket to Chrome tracing, so it is not strict JSON. Python 3 gzip returns bytes, but directory merge code compares/writes string literals and bytes together, which can fail unless run in a Python 2-like mode or adjusted. Unknown `Location` values raise `KeyError`. The output file handle is not closed explicitly. SAX parse errors are printed and processing continues with partial output.

## Test Signals
Use a tiny XML with ordered begin/end events to validate emitted `ts`, `dur`, `pid`, and `tid`; test gzipped file and directory merge paths; include missing end, unknown location, malformed XML, and Python 3 byte/string behavior.
