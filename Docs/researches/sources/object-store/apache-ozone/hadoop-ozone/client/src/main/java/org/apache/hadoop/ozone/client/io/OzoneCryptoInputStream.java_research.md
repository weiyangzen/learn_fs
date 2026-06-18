# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/OzoneCryptoInputStream.java

Purpose: This encrypted-bucket read stream wraps Hadoop `CryptoInputStream` and implements `PartInputStream` with a known part length. It adjusts reads to crypto buffer boundaries so decryption remains correct while callers receive exactly the requested range.

Important APIs and types: Public methods are the constructor, `getLength`, `getBufferSize`, and `read(byte[],int,int)`. Internal helpers `getNumBytesToRead`, `adjustReadPosition`, and `adjustNumBytesToRead` manage boundary alignment. It uses `LengthInputStream`, `CryptoCodec`, key/IV material, `CryptoStreamUtils`, and `PartInputStream` position/remaining methods.

Control flow: Reads compute the maximum bytes to read based on requested length, stream remaining bytes, and crypto buffer size. If current position is not buffer-aligned, the stream seeks backward and later discards leading bytes. If requested length ends before the buffer boundary, it reads more and later discards trailing bytes, seeking back by the trailing adjustment. Short reads after accounting for crypto boundaries throw an IOException.

State and persistence behavior: Runtime state includes fixed length, buffer size, key name, part index, and one-read adjustment counters. There are no writes or persistence. Position changes are delegated to the wrapped seekable crypto stream.

Dependencies and integration points: Used when reading keys in encrypted buckets, normally above `KeyInputStream`/`LengthInputStream`. It integrates Hadoop crypto codecs with Ozone multipart block reads and strict part-length accounting.

Risks: Boundary handling uses temporary byte arrays and copies, which can be expensive. Adjustment counters must reset after every adjusted read. Seeking backward for trailing bytes changes the underlying stream position in a non-obvious way. The code assumes `super.read` returns the full adjusted request or else treats it as corruption.

Test signals: Tests should cover aligned reads, unaligned start reads, unaligned end reads, both start and end adjustments together, end-of-part behavior, position after trailing adjustment, short-read exceptions, and crypto buffer size configuration.
