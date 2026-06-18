# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/test/java/org/apache/hadoop/ozone/debug/audit/parser/TestAuditParser.java

Purpose: `TestAuditParser` is the regression suite for the audit log parser CLI, covering load, built-in templates, custom SQL query, error propagation, and help output.

Important APIs and types: It uses `AuditParser`, picocli `CommandLine`, custom `IExceptionHandler2`, test resources `testaudit.log` and `testloadaudit.log`, temporary output directories, captured `System.out/err`, and AssertJ/JUnit assertions.

Control flow: `@BeforeAll` creates temp DB paths and loads the primary audit log. Each test redirects stdout/stderr, executes parser arguments through picocli handlers that rethrow parse/execution failures, and asserts output content. Tests query top commands, top users, top active seconds, arbitrary SQL count, invalid load behavior, and help text.

State and persistence behavior: The suite creates a SQLite audit DB in a temp directory and deletes the output base directory after all tests. Static stdout buffer `OUT` and parser instance are reused and reset per test.

Dependencies and integration points: It tests the audit parser command surface that lives outside this work item but is part of cli-debug.

Risks: The invalid load test expects an `ArrayIndexOutOfBoundsException` cause, which is brittle and exposes parser internals. Static buffers and parser state can leak if reset fails.

Test signals: Exact template rows, query count `12`, expected help usage prefix, and expected exception type/message for malformed load input.
