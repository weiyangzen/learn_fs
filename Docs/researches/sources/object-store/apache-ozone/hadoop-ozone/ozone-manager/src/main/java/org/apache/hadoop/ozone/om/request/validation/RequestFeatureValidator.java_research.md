
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/RequestFeatureValidator.java

Purpose: General annotation for request/response validators selected by runtime validation conditions and request type.

Important APIs and types: Runtime method annotation with `conditions`, `processingPhase`, and singular `requestType`; uses `ValidationCondition`, `RequestProcessingPhase`, and OM request `Type`.

Control flow: No executable code; reflection-based registry collects methods and later invokes them in pre- or post-processing phases when all selection criteria match.

State and persistence behavior: Runtime annotation metadata only.

Dependencies and integration points: Base annotation for validators that are not specifically client-version or layout-version bounded.

Risks: The annotation is not itself marked `@RegisterValidator` here, so discovery behavior depends on the broader validator registry implementation. Tests should verify annotated methods are found, signature-checked, and condition-filtered.
