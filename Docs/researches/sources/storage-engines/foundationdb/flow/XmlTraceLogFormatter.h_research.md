<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/XmlTraceLogFormatter.h -->
# sources/storage-engines/foundationdb/flow/XmlTraceLogFormatter.h
- Purpose: Declares the XML trace-log formatter implementation.
- Important APIs/types/functions: `XmlTraceLogFormatter final`, `addref`, `delref`, `getExtension`, `getHeader`, `getFooter`, `escape`, and `formatEvent`.
- Control flow: The header defines the formatter interface shape; runtime behavior is implemented in the `.cpp`.
- State and persistence behavior: Inherits reference-count state from `ReferenceCounted<XmlTraceLogFormatter>`. No other state is declared.
- Dependencies and integration points: Includes `flow/FastRef.h` and `flow/Trace.h`; implements `ITraceLogFormatter` selected by `Trace.cpp`.
- Risks: Public `escape()` accepts source by value, which copies input for mutation in the implementation. Formatter lifetime depends on Flow intrusive reference counting.
- Test signals: Compile-time interface conformance plus `/flow/XmlTraceEscape` and trace format selection cover this declaration.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/XmlTraceLogFormatter.h -->
