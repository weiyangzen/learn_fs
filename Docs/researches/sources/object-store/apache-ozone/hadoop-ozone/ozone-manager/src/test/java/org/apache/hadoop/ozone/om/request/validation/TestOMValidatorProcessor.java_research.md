# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/validation/TestOMValidatorProcessor.java

## Purpose
This class compile-tests `OmRequestFeatureValidatorProcessor`, the annotation processor that validates request-validator method signatures. It dynamically discovers all validator annotations annotated with `RegisterValidator` and then generates synthetic Java source for valid and invalid validator methods.

## Important APIs and Types
Important dependencies include Google compile-testing `javac()` and `CompilationSubject`, `JavaFileObjects`, `RegisterValidator`, `RequestProcessingPhase`, `Versioned`, `OzoneManagerProtocolProtos.Type`, `OMRequest`, `OMResponse`, `ValidationContext`, and processor error constants such as `ERROR_VALIDATOR_METHOD_HAS_TO_BE_STATIC`.

## Control Flow and State
The static `ANNOTATION_VERSION_CLASS_MAP` uses Reflections to find validator annotations whose `requestType` method returns `Type[]`, then maps each annotation to its version enum type from `applyBefore`. `annotatedClasses` expands each annotation/version pair into parameterized test arguments.

Positive tests verify annotations target only methods; correct pre-process validators return `OMRequest` with `(OMRequest, ValidationContext)` parameters; correct post-process validators return `OMResponse` with `(OMRequest, OMResponse, ValidationContext)`; exceptions are optional; and validator methods may be final, private, protected, or package-private as long as they are static. Negative tests compile generated sources with missing/extra parameters, wrong return types, wrong parameter types, invalid processing phase, invalid missing client/layout version, and multiple simultaneous errors. `compile` runs the processor and prints diagnostics. Helper methods generate imports, annotation strings, parameter lists, throws clauses, and method signatures.

## Dependencies and Integration Points
The tests integrate annotation metadata, enum versioning, request processing phases, generated source construction, and Java compiler diagnostics. They protect both OM client-version and layout-version validator annotations because discovery is generic.

## Risks and Test Signals
Risks include silently accepting malformed validator methods, requiring public visibility unnecessarily, missing multiple diagnostics, or failing when new validator annotations are added. Compile success/failure and exact diagnostic substring assertions are the primary signals.
