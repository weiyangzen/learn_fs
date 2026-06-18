# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/Fts5Tokenizer.java

## Purpose
`Fts5Tokenizer` is a Java wrapper for C-level `Fts5Tokenizer*` instances.

## Important APIs, Types, and Functions
It extends `NativePointerHolder<Fts5Tokenizer>` and has a JNI-only private constructor. The comments identify it as incomplete and completely untested.

## Control Flow
Intended tokenizer APIs would pass this wrapper into tokenizer methods, especially `fts5_tokenizer.xTokenize()`.

## State and Persistence Behavior
The wrapper does not own the native pointer. Tokenizer lifecycle is controlled by FTS5/native registration code.

## Dependencies and Integration Points
It depends on `NativePointerHolder` and is referenced by `fts5_tokenizer.xTokenize()`.

## Risks
The incomplete/untested status is the dominant risk. There is no Java-side registration implementation in this file, and lifecycle semantics must match FTS5 expectations to avoid dangling tokenizer pointers.

## Test Signals
No direct test coverage was found in `TesterFts5`; current FTS5 tests exercise auxiliary-function tokenization via `Fts5ExtensionApi.xTokenize()` instead.
