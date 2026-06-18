# sources/distributed-fs/xrootd/src/XrdCl/XrdClArg.hh

Purpose: defines operation argument wrappers for XrdCl's declarative API. An argument can be a plain value, a future value, or a forwarded value, while exposing a uniform `Get()` and conversion operator.

Important APIs/types: `ArgBase<T>`, nested `ValueHolder`, `PlainValue`, `FutureValue`, `FwdValue`, movable `Arg<T>`, and string specialization `Arg<std::string>` accepting `const char*`. It depends on `Fwd<T>` and `Optional<T>`.

Control flow/state: `Get()` throws if unset, otherwise returns a cached value. Future-backed arguments call `future.get()` once and cache into `Optional<T>`; forwarded arguments dereference `Fwd<T>` at access time. State is local to each wrapper and move-only through `unique_ptr`. Integration point is operation composition and chaining. Risks: blocking `future.get()` inside argument access, dangling forwarded values, implicit conversion hiding unset errors, and string specialization copying instead of moving in one constructor. Test signals: unset access exception, future caching, move construction/assignment, forwarded lifetime, and `const char*` conversion.
