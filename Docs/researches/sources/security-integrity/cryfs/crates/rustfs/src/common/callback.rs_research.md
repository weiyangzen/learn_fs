# sources/security-integrity/cryfs/crates/rustfs/src/common/callback.rs

Purpose: provides a generic callback pattern used by read-like FUSE APIs to force implementations to call back with borrowed data while returning the callback's result.

Important APIs: `Callback<T, R>::call(self, T) -> R` is the trait. `CallbackImpl<T, F>` wraps a `FnOnce(T)` and implements `Callback<T, ()>`.

Control flow and state: `CallbackImpl::new` stores the closure and a `PhantomData<T>`. `call` consumes the callback, preserving one-shot behavior and avoiding lifetime escape for borrowed buffers. The generic return type makes trait implementors unable to synthesize `R` without calling the callback.

Dependencies and integration: used in high-level and low-level `read` and `readlink` signatures so adapters can hand temporary byte or string slices to backend-specific reply objects. Re-exported from `lib.rs`.

Risks and tests: no runtime state and little failure surface. The pattern relies on type discipline; callers needing non-unit return values must implement their own callback type because `CallbackImpl` only covers `()`.
