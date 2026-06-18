# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/lang/XException.java

## Purpose
`XException` is the shared checked-exception base for the HttpFS support framework. It standardizes error-code enums, templated messages, and cause extraction.

## Important APIs, types, and functions
The public constructor accepts an `XException.ERROR` and varargs parameters. `getError()` returns the code. `ERROR#getTemplate()` supplies a `MessageFormat` template. Private helpers format messages as `ERROR: message` and treat the final vararg as the cause when it is a `Throwable`.

## Control flow
Construction validates the error code, formats the message, detects an optional cause, and delegates to `Exception`. If a code has no template, a positional template is synthesized from the argument count.

## State and persistence behavior
Each exception stores the error enum. There is no persistence beyond standard exception stack traces.

## Dependencies and integration points
`ServerException`, `ServiceException`, and `FileSystemAccessException` use this base. It relies on `MessageFormat`, so placeholders and quoting follow JDK formatting rules.

## Risks and edge cases
If the last message argument is intentionally a `Throwable` value rather than a cause, it will still be installed as the cause. Template/argument mismatches can produce confusing messages.

## Test signals
No direct test in this subset. Error-message assertions in server, filesystem, and Iceberg tests indirectly depend on stable formatting conventions.
