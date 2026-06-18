# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/StringWithByteString.java

## Purpose

`StringWithByteString` is an immutable value object that stores a Java `String` alongside its UTF-8 protobuf `ByteString` representation.

## APIs and control flow

The constructor requires non-null string and byte values. `valueOf(String)` returns null for null input or creates a new instance using `ByteString.copyFromUtf8`. Accessors return the stored string and bytes. `toString()` returns the string value.

## State, dependencies, and integration

State is final and immutable. The class depends on Google protobuf `ByteString` and JCIP `@Immutable`. It integrates with code that repeatedly needs both string and serialized forms without repeated conversion.

## Risks and test signals

The public constructor permits inconsistent string/bytes pairs if callers provide mismatched values; `valueOf` is the safe path. Tests should cover null behavior, UTF-8 conversion, constructor null checks, and `toString`.
