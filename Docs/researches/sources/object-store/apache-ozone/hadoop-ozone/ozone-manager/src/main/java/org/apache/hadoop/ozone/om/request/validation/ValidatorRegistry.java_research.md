# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/ValidatorRegistry.java

Purpose: `ValidatorRegistry` discovers OM request validator methods annotated with `RequestFeatureValidator` and indexes them by `ValidationCondition`, OM request `Type`, and `RequestProcessingPhase`. It is the reflection-backed lookup layer used by request validation code to decide which validators must run before or after request handling.

Important APIs and types: Constructors accept either a validator package or explicit `URL` collection. `validationsFor(List<ValidationCondition>, Type, RequestProcessingPhase)` returns unique `Method` instances. `initMaps(Collection<Method>)` reads annotation metadata and populates nested `EnumMap`s. It depends on `Reflections`, `Scanners.MethodsAnnotated`, `RequestFeatureValidator`, `ValidationCondition`, and `RequestProcessingPhase`.

Control flow: Construction scans the classpath, retrieves annotated methods, marks each method accessible, then stores each method under every declared condition. Lookup short-circuits on empty conditions or empty registry, then unions per-condition lists into a `HashSet` to avoid duplicate validator execution when several active conditions select the same method.

State and persistence behavior: State is purely in-memory: an `EnumMap<ValidationCondition, EnumMap<Type, EnumMap<RequestProcessingPhase, List<Method>>>>`. There is no DB persistence. Ordering is not guaranteed after unioning through `HashSet`, so validators should not rely on inter-validator order.

Dependencies and integration points: The class integrates OM-specific validation annotations with the generic Ozone request validation phase enum and protobuf request type enum. It depends on package/classpath scanning being configured to include all validator packages.

Risks and test signals: Risks include missing validators if classpath URLs are incomplete, nondeterministic ordering, and runtime failures from reflective invocation of incompatible method signatures elsewhere. Useful tests should cover duplicate condition unioning, pre/post separation, empty lookups, and package-scan discovery.
