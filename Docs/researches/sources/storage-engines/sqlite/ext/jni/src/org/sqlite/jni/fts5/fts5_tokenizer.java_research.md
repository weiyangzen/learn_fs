# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/fts5_tokenizer.java

## Purpose
`fts5_tokenizer` is a Java wrapper for the C `fts5_tokenizer` method table, currently focused on tokenization.

## Important APIs, Types, and Functions
It extends `NativePointerHolder<fts5_tokenizer>` and exposes native `int xTokenize(Fts5Tokenizer t, int tokFlags, byte[] pText, XTokenizeCallback callback)`.

## Control Flow
Given a native tokenizer instance and text bytes, `xTokenize()` delegates to the tokenizer's native `xTokenize` implementation and invokes the Java token callback for each token.

## State and Persistence Behavior
The wrapper does not own native tokenizer state. The `Fts5Tokenizer` argument represents the tokenizer instance whose lifecycle is external to this object.

## Dependencies and Integration Points
It depends on `NativePointerHolder`, `Fts5Tokenizer`, `XTokenizeCallback`, and `NotNull`. Commented C signatures show intended future create/delete integration.

## Risks
Creation and discovery of tokenizers are not implemented here, making this API incomplete. Incorrect lifecycle handling for `Fts5Tokenizer` could call into freed native state.

## Test Signals
No direct `TesterFts5` coverage was found for this wrapper; existing tokenization coverage uses `Fts5ExtensionApi.xTokenize()` instead.
