# sources/storage-engines/tikv/components/tikv_util/src/callback.rs

Purpose: provides a callback type and `must_call()` helper that guarantees a callback is invoked on drop if it was not called explicitly.

Important APIs: `Callback<T> = Box<dyn FnOnce(T) + Send>`, `must_call(callback, arg_on_drop)`, and the internal `MustCall<T, C, A>` guard that stores the callback and fallback argument factory.

Control flow: `must_call()` boxes a closure that takes ownership of `MustCall`; explicit invocation takes and calls the stored callback. If the boxed closure is dropped without invocation, `MustCall::drop()` calls `arg_on_drop()` and then the callback, unless the thread group is shutting down.

State and persistence: state is in-memory `Option` fields for the callback and fallback argument factory. There is no persistence.

Dependencies and integration: depends on `crate::thread_group::is_shutdown` to avoid firing callbacks during shutdown. It is useful for asynchronous code that must notify request owners on cancellation paths.

Risks: leaking the callback prevents `Drop`; panicking inside callback/drop fallback is dangerous because it occurs during drop; explicit calls use `unwrap()` on the stored callback and rely on `FnOnce` single-use semantics. Shutdown suppression means some callbacks intentionally do not fire during process teardown.

Test signals: local tests verify explicit invocation uses the supplied argument and dropping without invocation uses the fallback argument.
