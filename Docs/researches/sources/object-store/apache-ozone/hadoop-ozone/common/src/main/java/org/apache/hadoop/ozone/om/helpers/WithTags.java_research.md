<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/WithTags.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/WithTags.java

## Purpose

`WithTags` is a marker-style interface for OM objects that expose S3 object or bucket tags.

## Important APIs, Types, And Functions

It declares one method: `Map<String, String> getTags()`.

## Control Flow, State, And Persistence

The interface has no implementation or state. Implementing metadata classes decide how tags are stored, validated, serialized, and copied.

## Dependencies And Integration Points

It depends on Java `Map`. It integrates with object tagging APIs in `OzoneManagerProtocol` and S3-compatible tag retrieval/mutation paths.

## Risks And Test Signals

Implementations may return mutable maps unless they protect them. Tests belong on implementers and should cover tag immutability, UTF-8/key validation, protocol conversion, and delete-object-tagging behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/WithTags.java -->
