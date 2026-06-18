<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestProfileServlet.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestProfileServlet.java

Purpose: tests profile-output filename generation/validation to prevent unsafe filenames in `ProfileServlet`.

Important APIs/types/functions: `ProfileServlet.generateFileName`, `validateFileName`, `ProfileServlet.Output` values `FLAMEGRAPH`, `SVG`, `COLLAPSED`, and `ProfileServlet.Event.ALLOC`.

Control flow: valid tests generate filenames for several output types/events and pass them to validation. Negative tests prepend newline-containing or path-traversal strings and assert validation rejects them.

State and persistence behavior: no file I/O occurs in the test. It validates string safety before filenames could be used for profiler artifacts.

Dependencies and integration points: integrates profiler servlet naming with JUnit exception assertions.

Risks: filename validation is security-sensitive because profiler output may be served or written to disk. Tests cover newline and slash traversal, but additional platform-specific forbidden characters may need separate coverage.

Test signals: accepts generated filenames and rejects newline/path traversal inputs with `IllegalArgumentException`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestProfileServlet.java -->
