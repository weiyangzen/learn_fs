
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/RequestValidations.java

Purpose: Configures and executes the OM request validation framework for pre-process request validators and post-process response validators.

Important APIs and types: Holds validation package name, `ValidationContext`, and `ValidatorRegistry`; uses `RequestProcessingPhase.PRE_PROCESS/POST_PROCESS`, reflection `Method.invoke`, `OMRequest`, `OMResponse`, `OMException`, and `ServiceException`.

Control flow: `fromPackage` sets scan root, `withinContext` sets context, `load` creates the registry. `validateRequest` finds matching pre-process validators for current conditions and command type, invokes them in order, unwraps `OMException` causes, and otherwise wraps reflection failures in `ServiceException`. `validateResponse` similarly invokes post-process validators and wraps reflection failures.

State and persistence behavior: Maintains in-memory registry/context only. It does not persist validation state.

Dependencies and integration points: Sits in the OM request pipeline between raw protocol handling and operation-specific request classes, using `ValidationCondition` to decide compatibility behaviors.

Risks: `context` and `registry` must be initialized before validation; otherwise null failures occur. Invocation order comes from registry. Tests should cover condition filtering, chained request mutation, OMException unwrapping, post-response mutation, and illegal access/invocation errors.
