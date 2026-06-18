# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/Fts5Context.java

## Purpose
`Fts5Context` wraps C-level `Fts5Context*` values passed to FTS5 extension functions.

## Important APIs, Types, and Functions
It extends `NativePointerHolder<Fts5Context>` and adds no public methods.

## Control Flow
The native FTS5 bridge passes `Fts5Context` into `fts5_extension_function.call()` and `Fts5ExtensionApi` methods consume it.

## State and Persistence Behavior
The wrapper does not own its pointer. Its validity is tied to the current FTS5 auxiliary function invocation.

## Dependencies and Integration Points
It depends on `NativePointerHolder` and integrates with `Fts5ExtensionApi`, `fts5_extension_function`, and `fts5_api.xCreateFunction()`.

## Risks
Retaining the context after a callback can reference invalid native state. It is also not a general database handle; it is only meaningful with FTS5 extension APIs.

## Test Signals
`TesterFts5` exercises the wrapper through every custom auxiliary function, including rowid, column info, phrase iteration, auxdata, row count, query phrase, and tokenization calls.
