# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmDeleteKeys.java

Purpose: Client-side DTO describing a bulk key delete request: volume, bucket, and key names.

Important APIs/types/functions: Constructor sets the three fields; getters expose them.

Control flow and state: No branching. Fields are mutable only within the class but no setters are exposed.

State and persistence behavior: Request helper only. Actual deletion state is handled by OM request processing and DB tables.

Dependencies and integration points: Used by client/OM delete-key flows.

Risks: No defensive copy of key names and no null validation.

Test signals: Bulk delete request tests should verify key list propagation and caller-side validation for empty/null lists.
