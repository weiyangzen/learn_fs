# sources/storage-engines/foundationdb/flow/JsonTraceLogFormatter.cpp

## Purpose
Implements a simple JSON-lines TraceEvent formatter.

## Important APIs, Types, And Functions
`JsonTraceLogFormatter::{getExtension,getHeader,getFooter,formatEvent,addref,delref}` implement `ITraceLogFormatter`. Internal `escapeString()` escapes quotes, backslashes, newline, carriage return, printable characters, and nonprintable bytes as `\xNN`.

## Control Flow
`formatEvent()` streams a single object with all `TraceEventFields` key/value pairs as strings, comma-separated, and terminates with newline. Header and footer are empty; extension is `json`.

## State And Persistence Behavior
Formatter instances hold no mutable state. Output strings are passed to trace writers for persistence.

## Dependencies And Integration Points
Depends on `JsonTraceLogFormatter.h`, `Trace`, `FastRef`, `ReferenceCounted`, and standard streams. It is paired with `FileTraceLogWriter` or other trace writers.

## Risks And Edge Cases
The nonprintable escape uses `\xNN`, which is not standard JSON escaping, so strict JSON parsers may reject such output. All values are stringified, losing numeric JSON typing. Field order follows the input container order.

## Test Signals
No direct unit test. Trace file formatting, parser compatibility, and log ingestion are the main signals.
