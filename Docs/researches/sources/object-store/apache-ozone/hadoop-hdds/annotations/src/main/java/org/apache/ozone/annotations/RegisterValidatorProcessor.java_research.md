# sources/object-store/apache-ozone/hadoop-hdds/annotations/src/main/java/org/apache/ozone/annotations/RegisterValidatorProcessor.java

Purpose: Annotation processor for `RegisterValidator` annotations. It checks that annotated annotation types expose the required annotation methods used by Ozone request-validation registration.

Important APIs/types/functions: The required annotation methods are `applyBefore`, `requestType`, and `processingPhase`. `validateMethod` checks a method name, return element kind, and optional assignability to an expected interface. `validateArrayMethod` handles array-returning methods such as `requestType`. Error constants describe missing max-version, request-type, and processing-phase methods.

Control flow: `process` filters annotation types by simple name, retrieves elements annotated with `RegisterValidator`, and inspects only elements of kind `ANNOTATION_TYPE`. For each enclosed executable element, it updates booleans for required methods. Missing requirements produce compiler errors.

State and persistence behavior: No persistent runtime state; all validation is compiler diagnostic output.

Dependencies and integration points: Uses javac `Elements` and `Types` APIs and validates against `org.apache.hadoop.ozone.Version` and `RequestProcessingPhase`. It protects downstream OM validator annotation definitions from shape drift.

Risks: `validateArrayMethod` calls `types.asElement(method.getReturnType())` for the full array type in the assignability check when an expected interface is present; array types do not map like declared enum types. Current use passes `null` expected interface for `requestType`, avoiding that path. Non-annotation annotated elements are silently ignored. As with many processors, missing expected type elements could produce null-driven failures.

Test signals: Compile tests should include a valid registered annotation, annotations missing each required method, wrong enum/interface return types, array versus scalar request types, and non-annotation elements annotated with `RegisterValidator`.
