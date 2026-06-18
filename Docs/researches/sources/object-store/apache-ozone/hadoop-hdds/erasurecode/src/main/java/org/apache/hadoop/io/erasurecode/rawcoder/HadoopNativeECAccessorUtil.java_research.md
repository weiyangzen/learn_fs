<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/HadoopNativeECAccessorUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/HadoopNativeECAccessorUtil.java

## Purpose
This private utility bridges Ozone erasure-code wrappers to protected Hadoop native erasure-code implementation methods. It is placed in the Hadoop rawcoder package so it can access package/protected native encoder and decoder methods until Ozone adapts the native EC code directly.

## Important APIs, Types, And Functions
- `performEncodeImpl(NativeRSRawEncoder, ByteBuffer[], int[], int, ByteBuffer[], int[])` delegates Reed-Solomon native encoding.
- `performDecodeImpl(NativeRSRawDecoder, ByteBuffer[], int[], int, int[], ByteBuffer[], int[])` delegates Reed-Solomon native decoding.
- `performEncodeImpl(NativeXORRawEncoder, ByteBuffer[], int[], int, ByteBuffer[], int[])` delegates XOR native encoding.
- `performDecodeImpl(NativeXORRawDecoder, ByteBuffer[], int[], int, int[], ByteBuffer[], int[])` delegates XOR native decoding.
- The class is `final`, has a private constructor, and is annotated `@InterfaceAudience.Private`.

## Control Flow
Each public static method immediately forwards all buffers, offsets, data length, erased indexes, and output arrays to the corresponding Hadoop native encoder or decoder method. The utility performs no validation, copying, retry, fallback, or transformation. Any `IOException` from Hadoop native code is propagated to the caller.

## State And Persistence
The class is stateless. It mutates only the output `ByteBuffer` contents through the delegated native operations. It does not retain references, cache native handles, or persist metadata.

## Dependencies And Integration Points
The utility depends on Hadoop's `NativeRSRawEncoder`, `NativeRSRawDecoder`, `NativeXORRawEncoder`, and `NativeXORRawDecoder` classes, plus Java NIO `ByteBuffer`. Ozone native wrapper classes (`NativeRSRawEncoder`, `NativeRSRawDecoder`, `NativeXORRawEncoder`, and `NativeXORRawDecoder` in the `org.apache.ozone.erasurecode.rawcoder` package) call this utility from their protected implementation methods. The module POM's Hadoop Common dependency supplies the Hadoop native classes.

## Risks And Edge Cases
This file relies on a package-level access workaround by using the Hadoop package name inside the Ozone module. Hadoop API changes to method signatures, visibility, or package structure can break compilation. Because all validation is delegated, malformed offset arrays, buffer sizing mistakes, direct-vs-heap buffer issues, or native library linkage errors surface from lower layers. The bridge should stay minimal; adding behavior here could diverge from Hadoop native EC semantics.

## Test Signals
Native erasure-code encode/decode tests should exercise both RS and XOR wrappers, including fallback behavior when native code is unavailable. Compilation against the selected Hadoop Common version is itself an important compatibility signal. ByteBuffer round-trip tests with erased indexes verify that offsets and data length are passed through correctly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/HadoopNativeECAccessorUtil.java -->
