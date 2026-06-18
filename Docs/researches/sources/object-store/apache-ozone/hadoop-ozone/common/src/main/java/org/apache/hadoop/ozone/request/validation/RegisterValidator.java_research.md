# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/request/validation/RegisterValidator.java

Purpose: Meta-annotation for registering request validator annotations. It identifies annotations that a reflection or annotation-processing system should treat as validator descriptors.

Important APIs and types: Runtime-retained annotation targeting annotation types. Constants define required method names: `applyBefore`, `requestType`, and `processingPhase`.

Control flow: No direct logic. `RegisterValidatorProcessor` or runtime discovery scans annotations annotated with `@RegisterValidator` and expects the named methods with documented return types.

State and persistence behavior: Annotation metadata is stored in class files and retained at runtime; no application persistence.

Dependencies and integration points: Tied to Ozone layout-version-aware request validation, `Versioned`, `RequestProcessingPhase`, and server request handling code that discovers validators.

Risks: The contract is name-based, so typos or signature mismatches in downstream validator annotations can fail at processing/discovery time. Runtime retention has reflection cost but enables dynamic discovery.

Test signals: Annotation processor tests should reject invalid validator annotations and accept valid annotations with the three required methods.
