# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/ProtobufUtils.java

## Purpose

`ProtobufUtils` provides small helpers for converting common Java types to HDDS protobuf types and for computing protobuf serialized sizes.

## APIs and control flow

`toProtobuf(UUID)` builds `HddsProtos.UUID` from most and least significant bits. `fromProtobuf` reverses the conversion. `computeRepeatedStringSize` wraps protobuf `computeStringSizeNoTag` for repeated string element sizing. `computeLongSizeWithTag` delegates to `CodedOutputStream.computeInt64Size`.

## State, dependencies, and integration

The class is stateless. It depends on Google protobuf `CodedOutputStream`, Java `UUID`, and HDDS protobufs. It integrates with serialization code that needs exact protobuf size estimates or UUID wire conversion.

## Risks and test signals

Null inputs are not guarded and will throw `NullPointerException`. Tests should cover UUID round trips, known serialized size values, field-number handling, and negative long sizing.
