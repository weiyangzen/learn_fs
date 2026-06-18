<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/WithMetadata.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/WithMetadata.java

## Purpose

`WithMetadata` is a base mixin for OM metadata objects that need immutable custom key-value metadata.

## Important APIs, Types, And Functions

The abstract class stores an `ImmutableMap<String,String>` and exposes final `getMetadata`. The nested `Builder` supports `addMetadata`, `addAllMetadata`, `setMetadata`, and direct access to the `MapBuilder`.

## Control Flow, State, And Persistence

Subclasses call the builder constructor to snapshot metadata into an immutable map. Metadata persistence is implemented by subclasses that serialize the map into their protobuf fields, such as volume, bucket, and key info.

## Dependencies And Integration Points

It depends on Guava `ImmutableMap`, `MapBuilder`, and JCIP `@Immutable`. It is inherited by `WithObjectID` and many OM helper metadata classes.

## Risks And Test Signals

The builder remains mutable until build time, and null key/value handling depends on `MapBuilder`. Tests should cover metadata copy construction, replacing maps, null/empty maps, immutability of built objects, and subclass protobuf preservation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/WithMetadata.java -->
