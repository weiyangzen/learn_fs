## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/StringUtils.java

Purpose: HDDS byte/string conversion and simple lexical string boundary helpers.

Important APIs: UTF-8 byte array and `ByteBuffer` decoding, byte-to-hex formatting with optional max byte count and overflow ellipsis, UTF-8 string-to-bytes, one-character lexicographic lower/higher transformations, and `getFirstNChars`.

Control flow: `bytes2Hex(ByteBuffer,int)` duplicates as read-only, enforces positive max, formats uppercase two-digit hex separated by spaces, and appends `...` when truncated. Lexicographic helpers reject null/empty input and prevent underflow/overflow of the last character.

State/persistence: no mutable state. Dependencies: Java NIO charset, Ratis-shaded Netty `Unpooled`, Ratis `Preconditions`.

Integration points: debugging binary buffers, key range calculations, and prefix display. Risks: lexical helpers modify only the last UTF-16 code unit, so they are not Unicode-collation aware; `getFirstNChars` returns the original string when `n` exceeds length but will throw through `substring` for negative `n`; hex formatting via `String.format` is relatively expensive. Test signals: ByteBuffer position preservation, max/truncation behavior, invalid max, min/max character edge cases, null handling, and surrogate-pair inputs if used with non-ASCII keys.
