# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/content.py

Purpose: MIME-like content abstraction for attaching diagnostics, tracebacks, files, streams, JSON, and text to test results.

Important APIs, types, and functions: `Content` stores a `ContentType` and byte iterator callback, with `iter_bytes()`, `iter_text()`, and `as_text()`. `StackLinesContent`, `TracebackContent`, and `StacktraceContent()` produce traceback content. Helpers include `json_content()`, `text_content()`, `content_from_file()`, `content_from_stream()`, `content_from_reader()`, and `attach_file()`.

Control flow: file/stream helpers create lazy readers unless `buffer_now=True`, in which case bytes are read immediately and captured in memory. Traceback helpers filter internal unittest/testtools frames when configured, format tracebacks with `traceback.TracebackException`, and encode UTF-8 chunks. `attach_file()` builds a content object and calls `detailed.addDetail()`.

State and persistence: `Content` may defer reading external files/streams until result serialization, so state can depend on later filesystem contents unless buffered. No data is written.

Dependencies and integration points: depends on `codecs`, `json`, `os`, `traceback`, `testtools.compat`, and `testtools.content_type`. Integrated throughout `TestCase` failure reporting and fixture detail gathering.

Risks and test signals: lazy file content can fail if cleanup deletes the file before serialization; the docstring calls this out. `Content.__eq__` loads all content into memory. Test signals include attached traceback details, UTF-8 text decoding, JSON content, and file attachments with both buffered and lazy modes.
