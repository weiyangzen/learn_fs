# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/strfunc.h

Purpose: This header provides small string helpers that work across RapidJSON encoding character types.

Important APIs and functions: `StrLen(const Ch*)` counts code units in a null-terminated string and returns `SizeType`. `CountStringCodePoint<Encoding>()` decodes a fixed-length encoded string and returns the number of Unicode codepoints through an output parameter.

Control flow: `StrLen()` advances until the zero terminator. `CountStringCodePoint()` wraps the input in `GenericStringStream<Encoding>`, decodes until the stream reaches the provided end pointer, increments a count for each valid codepoint, and returns false if decoding fails.

State and persistence behavior: No persistent state. The functions only read caller-provided memory and, for codepoint counting, update `outCount`.

Dependencies and integration points: It includes `stream.h` for `GenericStringStream` and depends on encoding `Decode()` methods. Pretty writer convenience overloads use `StrLen`; schema/string validation and length-related logic can use codepoint counting.

Risks: `StrLen()` counts code units, not Unicode characters, which matters for UTF-8 and UTF-16. `CountStringCodePoint()` assumes the supplied length points to complete encoded data; truncated sequences return false after consuming through the temporary stream.

Test signals: Cover narrow and wide strings, embedded null behavior through length-aware paths, UTF-8 multibyte counts, invalid encoding rejection, and distinction between code-unit length and codepoint count.
