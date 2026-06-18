# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/InconsistentStorageStateException.java

## Purpose

`InconsistentStorageStateException` is an `IOException` subtype for unrecoverable local filesystem or storage metadata inconsistencies. It is annotated private/evolving and is intended for internal HDDS/Ozone storage initialization and validation paths.

## APIs and control flow

The string constructor passes a description directly to `IOException`. The file constructor builds a message in the form `Directory <path> is in an inconsistent state: <descr>`. `getFilePath(File)` prefers `getCanonicalPath()` and falls back to `getPath()` if canonicalization fails.

## State, dependencies, and integration

The class has no mutable state beyond standard exception fields. It depends only on `java.io.File`, `IOException`, and HDDS audience/stability annotations. It integrates with callers that need a typed signal that storage layout/state cannot be safely recovered.

## Risks and test signals

The canonical-path failure is silently ignored, which is appropriate for error reporting but can hide path resolution issues. Tests should check message formatting, canonical fallback behavior, and that callers do not swallow this exception in paths requiring manual intervention.
