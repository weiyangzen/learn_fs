## sources/storage-engines/foundationdb/flow/actorcompiler_py/errors.py

Purpose: this tiny Python module defines the location-aware exception type shared by the Python parser and compiler.

Important APIs: `ActorCompilerError(source_line, message, *args)` formats optional arguments with `str.format`, stores `source_line`, and renders as `<message> (line <source_line>)`.

Control flow: no complex flow; exceptions are raised by parser/compiler code and caught by the CLI.

State and persistence behavior: exception objects carry source-line state only in memory. No persistence.

Dependencies and integration points: imported by `actor_parser.py`, `actor_compiler.py`, and `__main__.py`. The CLI maps it to FAC1000 diagnostics.

Risks: because messages are formatted with Python `str.format`, literal braces in messages must be escaped. Source line `0` is used for some internal errors and may produce less useful user diagnostics.

Test signals: tests should verify message formatting, string rendering, source-line retention, and CLI FAC1000 output.
