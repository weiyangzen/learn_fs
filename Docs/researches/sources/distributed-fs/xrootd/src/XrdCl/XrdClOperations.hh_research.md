# sources/distributed-fs/xrootd/src/XrdCl/XrdClOperations.hh

## Purpose

This header defines the XrdCl operation pipeline DSL. It represents once-use operations, chains them with `|`, binds handlers with `>>`, runs them asynchronously or synchronously, and supports final operations.

## Important APIs, Types, And Functions

`Operation<HasHndl>` is the abstract base with `ToString`, `Move`, `ToHandled`, `Run`, `RunImpl`, and `AddOperation`. `PipelineHandler` is the internal response handler that advances the pipeline. `Pipeline` owns the first operation and exposes chaining, conversion, `Run`, and static controls `Stop`, `Repeat`, `Replace`, and `Ignore`. Helper functions `Async` and `WaitFor` execute a pipeline. `ConcreteOperation<Derived, HasHndl, HdlrFactory, Args...>` is the CRTP base for concrete operations and implements `>>`, `|`, `Move`, `ToHandled`, and per-operation timeout setting.

## Control Flow

Concrete operations start unhandled. `operator>>` wraps a user handler in `PipelineHandler` and returns a handled operation. `operator|` ensures the left side has a pipeline handler, appends the right operation, and returns a handled operation. `Pipeline::Run` creates a promise/future pair, releases the first operation, prepares final callbacks, and invokes `Operation::Run`.

`Operation::Run` assigns timeout/promise/final/current operation to the handler, releases handler ownership, calls the concrete `RunImpl`, and schedules a `ResponseJob` if `RunImpl` fails synchronously or throws a mapped exception.

## State And Persistence

Operations are deliberately once-use. Move construction invalidates the source, and invalid operations should not be reused. Pipeline state is in `unique_ptr` operations/handlers plus a `std::future<XRootDStatus>`. No disk or long-term persistence is involved.

## Dependencies And Integration Points

The header pulls in response types, operation handlers, argument helpers, timeouts, final operations, `ResponseJob`, `JobManager`, `PostMaster`, and `DefaultEnv`. Concrete operation classes elsewhere derive from `ConcreteOperation` and provide `RunImpl`.

## Risks

`Pipeline::Run` has `if( !operation ) std::logic_error("Empty pipeline!")` without `throw`, so an empty pipeline can continue to dereference null. `ConcreteOperation::Timeout` returns `std::move(*me)`, invalidating the current object by convention but not marking `valid` itself. The once-use validity model depends on move constructors being used correctly. `Operation::Run` assumes `DefaultEnv::GetPostMaster()->GetJobManager()` exists when scheduling synchronous failure responses.

## Test Signals

Tests should verify invalid reuse throws, handler binding, pipeline chaining across handled/unhandled operations, final operation movement, per-operation timeout propagation, sync failure scheduling, exception mapping, empty pipeline behavior, `Async` future completion, and `WaitFor` blocking semantics.
