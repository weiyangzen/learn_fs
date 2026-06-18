# sources/storage-engines/foundationdb/flow/coveragetool/Program.cs

Purpose: command-line tool that scans source files for Flow coverage macros and writes an XML inventory of coverage cases.

Important APIs/types/functions: `CoverageCase`, `ParseException`, `Main`, `ParseOutput`, `WriteOutput`, `ParseSource`, and `FindComment`.

Control flow: `Main` validates args, reads existing output when input list matches, detects changed files by modification time, reuses unchanged cases, parses changed sources, and writes XML. `ParseSource` uses a regex to find `TEST`, `INJECT_FAULT`, and `SHOULD_INJECT_FAULT` invocations outside `#define` lines, then requires each case to have a unique non-empty trailing `//` comment.

State/persistence: persists cases and input paths in the XML output file. Incremental behavior depends on output timestamp and input list equality.

Dependencies/integration: C#/.NET LINQ, XML, regex, file I/O. It supports FoundationDB code coverage/probe tooling by enforcing comment uniqueness.

Risks: regex parsing is shallow and can miss multiline or unusual macro invocations. Incremental reuse trusts timestamps. Duplicate detection is per parsed changed file batch, not obviously global across reused unchanged cases.

Test signals: exit code `0` on success, `1` on parse validation failure, `100` on usage error; verbose output is controlled by `VERBOSE`.
