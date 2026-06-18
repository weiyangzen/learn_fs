# sources/object-store/apache-ozone/hadoop-hdds/annotations/src/main/java/org/apache/ozone/annotations/OmRequestFeatureValidatorProcessor.java

Purpose: Implements a javac annotation processor that validates Ozone Manager request feature validator methods annotated with `OMClientVersionValidator` or `OMLayoutVersionValidator`.

Important APIs/types/functions: The processor supports two annotation types and Java 8 source. It validates that annotated elements are methods, are static, have the right return type for the annotation processing phase, and have expected parameters. Constants define required fully qualified types for `OMRequest`, `OMResponse`, and `ValidationContext`. `ProcessingPhaseVisitor` extracts enum values for `PRE_PROCESS` and `POST_PROCESS`.

Control flow: `process` filters supported annotations by simple name, then passes matching annotated elements to `processElements`. For each annotation mirror on an element, `validateAnnotatedMethod` reads `processingPhase`, checks method kind and static modifier, validates return type, and validates parameter count/order. Errors are emitted with `processingEnv.getMessager()`.

State and persistence behavior: No persistent state beyond constants. Diagnostics are reported into the compiler round; returning `false` allows other processors to also process these annotations.

Dependencies and integration points: Integrates with Ozone OM request validation annotations and javac's annotation-processing API. It relies on type string equality against generated protobuf nested classes.

Risks: `validateAnnotatedMethod` casts to `ExecutableElement` after emitting a non-method error, so an incorrectly annotated class/field may still cause `ClassCastException` instead of a clean diagnostic. The processor loops over all annotation mirrors on an element, not only the matched annotation, so unrelated annotations lacking `processingPhase` may be treated as post-process by default. Default annotation values absent from `getElementValues()` can make `isPreprocessor` default false.

Test signals: Compile-failure tests should cover non-static validators, wrong parameter counts, wrong return types for pre/post phases, missing or default processing phase behavior, and non-method annotated elements.
