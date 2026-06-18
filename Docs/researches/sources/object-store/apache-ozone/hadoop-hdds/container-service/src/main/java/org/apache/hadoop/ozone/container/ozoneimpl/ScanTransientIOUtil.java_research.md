# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ScanTransientIOUtil.java

Purpose: identifies scan failures caused only by transient file-descriptor exhaustion so scanner callers can distinguish environmental IO pressure from container corruption.

Important APIs and functions: `scanErrorsAreOnlyTooManyOpenFiles(ScanResult)` returns true only when the scan has at least one error and every error's exception chain matches `too many open files`. `isTooManyOpenFiles(Throwable)` walks up to 64 causes, tracks visited exceptions by identity to avoid cause-cycle loops, and delegates to `matchesTooManyOpenFiles`. Matching checks `FileSystemException.getReason()` first and then the generic exception message, case-normalized with `Locale.ROOT`.

Control flow and state: the class is stateless and final. The only state is local traversal state for cycle detection and a depth limit. A clean scan explicitly returns false, which prevents callers from treating absence of errors as a transient failure.

Dependencies and integration: depends on `ScanResult` and standard Java exception types. It is meant for scanner decision logic in `ozoneimpl` where corruption marking should be avoided for known transient resource exhaustion.

Risks and test signals: matching is message-based and therefore platform/JDK dependent. Tests should cover `FileSystemException` reasons, nested causes, null throwables/messages, cause cycles, mixed transient and non-transient scan errors, and uppercase/localized variants of the target text.
