# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/annotation/Experimental.java

## Purpose
Defines a source-retained annotation used to label JNI APIs that are unstable and may change or be removed.

## Important APIs, Types, And Functions
`@Experimental` is documented, retained only in source, and targets methods, constructors, and types. It has no members.

## Control Flow
No runtime flow exists because the annotation is not retained in class files for runtime reflection.

## State And Persistence Behavior
No state or persistence. It affects documentation and compile-time source readability only.

## Dependencies And Integration Points
Depends on `java.lang.annotation`. Used by `CApi` to mark direct `ByteBuffer`/NIO related APIs and feature probes.

## Risks And Edge Cases
Because retention is `SOURCE`, tools running on bytecode cannot detect it. Client code must not treat annotated APIs as stable even if they compile.

## Test Signals
Compile and javadoc generation are the main signals. Runtime tests will not observe this annotation.
