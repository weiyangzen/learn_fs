# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/XTokenizeCallback.java

## Purpose
`XTokenizeCallback` models callbacks receiving tokens from FTS5 tokenization APIs.

## Important APIs, Types, and Functions
It declares `int call(int tFlags, byte[] txt, int iStart, int iEnd)`, where flags describe token properties, `txt` contains token bytes, and offsets identify the token range in the original input.

## Control Flow
`Fts5ExtensionApi.xTokenize()` or `fts5_tokenizer.xTokenize()` invokes the callback once per token. The returned int is a SQLite result code controlling continuation/error.

## State and Persistence Behavior
No state is stored. Implementations typically append decoded tokens to local lists or build an index.

## Dependencies and Integration Points
It is used by `Fts5ExtensionApi.xTokenize()` and `fts5_tokenizer.xTokenize()` and pairs with constants in `Fts5`.

## Risks
Callbacks must decode bytes with the intended encoding and respect offsets. Returning non-OK values changes native control flow.

## Test Signals
`TesterFts5.test6()` registers an auxiliary function that tokenizes input text, joins decoded UTF-8 tokens with plus signs, and validates expected token lists for simple text and punctuation/case cases.
