<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/XmlTraceLogFormatter.cpp -->
# sources/storage-engines/foundationdb/flow/XmlTraceLogFormatter.cpp
- Purpose: Implements XML formatting for Flow trace events and validates escaping behavior.
- Important APIs/types/functions: `XmlTraceLogFormatter::addref/delref`, `getExtension`, `getHeader`, `getFooter`, `escape`, `formatEvent`, and test `/flow/XmlTraceEscape`.
- Control flow: `formatEvent()` writes one self-closing `<Event ... />` element, escaping each key and value. `escape()` replaces XML meta characters, newline/carriage-return/NUL with safe text, and logs stripped NUL characters. The test creates a trace event with XML-like junk and asserts escaped output contains no raw angle brackets.
- State and persistence behavior: Formatter has no mutable persistent state. Static `xmlIllegalCharSeverity` is adjusted by the test with `ScopeExit`. Output strings are written by `TraceLog` to trace files.
- Dependencies and integration points: Implements `ITraceLogFormatter` consumed by `Trace.cpp`. Depends on Flow `TraceEvent`, `ScopeExit`, `UnitTest`, and reference counting.
- Risks: The comment explicitly says output is not guaranteed to make arbitrary remote text semantically valid XML beyond escaping meta characters. Logging from `escape()` on illegal characters can recurse if not controlled by severity/suppression.
- Test signals: `/flow/XmlTraceEscape` covers heavy meta-character escaping. Trace-file smoke tests should verify headers, footers, and event formatting.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/XmlTraceLogFormatter.cpp -->
