# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/request/validation/RequestProcessingPhase.java

Purpose: Enum describing when a registered request validator should run relative to generic request processing.

Important APIs and types: Values are `PRE_PROCESS` and `POST_PROCESS`.

Control flow: No logic. Validation dispatchers use the enum to choose hook points before or after request handling.

State and persistence behavior: Stateless enum; values may appear in generated metadata or reflected annotation values.

Dependencies and integration points: Used by `RegisterValidator`-annotated annotations and validation registries in OM request processing.

Risks: Adding or renaming values affects annotations, generated validator indexes, and dispatch logic.

Test signals: Validator discovery tests should route methods into the expected pre/post buckets.
