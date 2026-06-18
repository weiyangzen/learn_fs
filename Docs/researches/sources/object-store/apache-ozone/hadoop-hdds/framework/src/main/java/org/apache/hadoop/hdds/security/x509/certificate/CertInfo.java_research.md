# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/CertInfo.java

## Purpose

`CertInfo` wraps an `X509Certificate` with the timestamp at which it was persisted in the database. It provides a DB codec and stable ordering by timestamp for certificate metadata records.

## Important APIs, Types, and Functions

Static `CODEC` is a `DelegatedCodec` over `CertInfoProto`, converting through `fromProtobuf` and `getProtobuf`. `COMPARATOR` orders by `getTimestamp`. Public accessors expose certificate and timestamp. `compareTo`, `equals`, `hashCode`, and `toString` implement value-like semantics. The nested `Builder` sets certificate and timestamp.

## Control Flow

Serialization converts the certificate to PEM with `CertificateCodec.getPEMEncodedString`; deserialization parses PEM with `CertificateCodec.getX509Certificate`. Conversion failures are wrapped in `CodecException`.

## State and Persistence Behavior

The object is immutable after construction. Its persistence behavior is explicitly protobuf-backed via `CertInfoProto`, so it can be stored in Ozone metadata DB tables using `Codec<CertInfo>`.

## Dependencies and Integration Points

It integrates certificate metadata with HDDS DB codecs, `HddsProtos.CertInfoProto`, `CertificateCodec`, and SCM security exceptions.

## Risks and Edge Cases

`Builder.build()` does not validate non-null certificate input. `toString()` calls `x509Certificate.toString()` and can be verbose. Ordering only by timestamp can compare distinct certificates as equal in `compareTo` if persisted at the same millisecond.

## Test Signals

Round-trip codec tests with real PEM certificates, malformed protobuf PEM handling, equality/hash behavior, timestamp ordering, and null-builder field behavior should cover the class.
