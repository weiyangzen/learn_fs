# sources/distributed-fs/xrootd/src/XrdCl/XrdClAnyObject.hh

Purpose: provides a lightweight type-safe holder for object pointers without a Boost dependency. XrdCl uses it to pass channel/query/response data across interfaces that cannot be templated.

Important APIs/types: `AnyObject::Set(Type object, bool own)`, `Get(Type&)`, `Has<Type>()`, `HasOwnership()`, internal abstract `Holder`, templated `ConcreteHolder`, and helper `To<T>(AnyObject&)`.

Control flow/state: `Set(nullptr)` clears the holder; otherwise it replaces the holder, records `typeid(Type)`, and conditionally owns deletion. The destructor calls the held pointer's `delete` only when `pOwn` is true, then deletes the holder. Dependencies are RTTI and C string comparison of `type_info::name()`. Risks: only pointer-like types are safe because `ConcreteHolder::Delete` does `delete pObject`; type matching via `type_info::name()` strings is fragile across ABI boundaries; `To<T>` dereferences without null validation. Test signals: owned/non-owned pointer lifecycle, wrong-type `Get`, null reset, and use through channel/query paths.
