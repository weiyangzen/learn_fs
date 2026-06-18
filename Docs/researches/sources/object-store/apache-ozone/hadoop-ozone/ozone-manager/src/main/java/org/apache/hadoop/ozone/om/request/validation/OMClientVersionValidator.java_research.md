
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/OMClientVersionValidator.java

Purpose: Annotation for validator methods that apply based on the client protocol version of an OM request.

Important APIs and types: Runtime method annotation targeted at methods, marked with `@RegisterValidator`; attributes are `processingPhase`, `requestType[]`, and `applyBefore` of type `ClientVersion`.

Control flow: No executable code in the annotation itself. Validator registry reflection discovers annotated static methods and applies them when request client version precedes the configured bound.

State and persistence behavior: No persistence. Annotation metadata is retained at runtime.

Dependencies and integration points: Integrates with `ValidatorRegistry`, `VersionExtractor`, `RequestProcessingPhase`, and request validation framework for older-client compatibility.

Risks: Annotated methods must follow fixed static signatures documented in Javadoc; misuse is detected at registry/runtime rather than compile time. Tests should cover registry discovery and version-bound selection.
