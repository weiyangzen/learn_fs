# sources/storage-engines/foundationdb/contrib/TraceLogHelper/JsonParser.cs

Purpose: parses line-delimited JSON FoundationDB traces into `Event` objects.

Important APIs/functions: static `JsonParser.Parse(Stream, file, keepOriginalElement, startTime, endTime, samplingFactor, nonFatalErrorMessage)` and private `ParseEvent`.

Control flow: reads one JSON line at a time, converts it to `XElement` via `JsonReaderWriterFactory`, optionally samples, handles `TrackLatestType=Rolled` by using `OriginalTime`, filters by time range, interns common strings, and stores remaining fields in `DDetails`.

State and persistence: read-only stream iteration; static `Random` controls sampling.

Dependencies and integration: System.Runtime.Serialization.Json, XML LINQ/XPath, and `Event`.

Risks and test signals: malformed JSON throws and aborts; the nonfatal callback parameter is unused; XPath lookups assume required fields exist. Test rolled events, sampling, time filtering, missing Severity/ID defaults, and malformed lines.
