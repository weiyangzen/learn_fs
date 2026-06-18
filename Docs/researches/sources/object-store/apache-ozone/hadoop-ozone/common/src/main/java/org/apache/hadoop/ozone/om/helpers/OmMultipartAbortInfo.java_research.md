# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartAbortInfo.java

Purpose: Aggregates the OM DB keys and metadata needed to abort a multipart upload.

Important APIs/types/functions: Builder sets multipart key, multipart open key, `OmMultipartKeyInfo`, and `BucketLayout`. Getters expose all fields. Equality/hash include all fields.

Control flow and state: Immutable after build. No validation in builder.

State and persistence behavior: Does not persist itself; it carries identifiers and persisted multipart metadata used by abort request processing to remove table entries and cleanup blocks.

Dependencies and integration points: Used by multipart abort logic across legacy/object-store/FSO layouts.

Risks: Equality assumes non-null fields and will throw if partially built objects are compared. Missing bucket layout can break caller table selection.

Test signals: Abort request tests should verify correct multipart key/open-key selection for each layout, metadata cleanup, and equality for complete objects.
