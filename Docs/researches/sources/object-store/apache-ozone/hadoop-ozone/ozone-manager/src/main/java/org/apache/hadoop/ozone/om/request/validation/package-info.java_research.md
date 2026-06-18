# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/package-info.java

Purpose: This package documentation defines the design intent for OM request feature validation: add condition-specific request behavior without cluttering core request handlers.

Important APIs and types: It documents `ValidationCondition`, `RequestFeatureValidator`, OM protobuf `Type`, and the expectation that validators are simple stateless methods tied to one request type.

Control flow: The package-level flow is reflection discovery of annotated methods, selection by condition, request type, and phase, and execution to reject or rewrite requests around upgrades or client-version compatibility.

State and persistence behavior: The documented validators should be stateless and do not persist data directly. Persistent effects happen later in normal request processing after validation succeeds.

Dependencies and integration points: The package integrates request classes, upgrade/layout state, client version checks, and the shared request validation framework.

Risks and test signals: The documentation warns against complex multi-request validators. Tests should confirm validators stay simple, have proper annotations, and are discovered for the intended condition and phase.
