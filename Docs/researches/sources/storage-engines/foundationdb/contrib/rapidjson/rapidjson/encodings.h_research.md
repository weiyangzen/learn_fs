# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/encodings.h

Purpose: This header defines RapidJSON's encoding concept implementations and transcoding glue for Unicode and byte streams. It covers UTF-8, UTF-16 native, UTF-16LE/BE, UTF-32 native, UTF-32LE/BE, ASCII, runtime-selected `AutoUTF`, and `Transcoder` templates used by the reader, writer, encoded streams, schema regex, and pointer URI fragment handling.

Important APIs and types: Key types are `UTF8`, `UTF16`, `UTF16LE`, `UTF16BE`, `UTF32`, `UTF32LE`, `UTF32BE`, `ASCII`, `UTFType`, `AutoUTF`, and `Transcoder`. Each encoding exposes `Ch`, `supportUnicode`, `Encode`, `EncodeUnsafe`, `Decode`, `Validate`, `TakeBOM`, `Take`, `PutBOM`, and `Put`. UTF-8 uses `GetRange()` classification for DFA-style validation. `AutoUTF` dispatches through static function-pointer tables keyed by stream `GetType()`.

Control flow: Encode paths branch by codepoint range and emit one or more code units. Decode paths consume stream code units, validate continuation/surrogate/range rules, and return false on malformed input. Byte-order variants explicitly compose or decompose little- and big-endian byte sequences and skip BOMs when present. `Transcoder<Source, Target>` decodes a codepoint from the source and encodes it to the target, while the same-encoding specialization copies one code unit and delegates validation to the encoding.

State and persistence behavior: There is no persistent storage. State lives only in caller-provided streams and static lookup tables. Invalid encodings consume bytes/code units as they validate, so callers depend on parse-error propagation rather than rewind.

Dependencies and integration points: It depends on `rapidjson.h`, stream `Put`/`Take` concepts, and `PutUnsafe` from `stream.h`. Reader string parsing, writer output, encoded input/output streams, regex decoding, and pointer percent transcodes all rely on these exact semantics.

Risks: UTF decoding is boundary-sensitive: overlong UTF-8, surrogate halves, invalid continuations, BOM handling, and stream truncation can all corrupt parse behavior if changed. `ASCII::supportUnicode = 0` means non-ASCII data must be rejected or escaped by callers. `AutoUTF` assumes valid runtime `UTFType` indexes.

Test signals: Cover UTF-8 boundary codepoints, invalid UTF-8 classes, UTF-16 surrogate pairs and lone surrogates, UTF-32 values above `0x10FFFF`, BOM detection for every endian variant, same-encoding copy versus validate behavior, ASCII rejection above `0x7F`, and `AutoUTF` dispatch for each `UTFType`.
