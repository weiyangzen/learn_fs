
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/OMLayoutVersionValidator.java

Purpose: Annotation for validator methods that apply based on OM metadata layout version and feature finalization state.

Important APIs and types: Runtime method annotation targeted at methods, marked with `@RegisterValidator`; attributes are `processingPhase`, `requestType[]`, and `applyBefore` of type `OMLayoutFeature`.

Control flow: The annotation contributes metadata consumed by validator discovery and dispatch; actual validation runs in annotated static methods.

State and persistence behavior: No direct state beyond runtime annotation metadata.

Dependencies and integration points: Connects request handlers and compatibility validators to the layout-version manager through `ValidatorRegistry`, `VersionExtractor`, and `ValidationContext`.

Risks: Multiple request types are discouraged for maintainability. Incorrect signatures or bounds can skip critical pre-finalization validation. Tests should cover discovery and dispatch around layout versions.
