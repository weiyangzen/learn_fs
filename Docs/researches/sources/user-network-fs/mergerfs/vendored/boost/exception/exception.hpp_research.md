# sources/user-network-fs/mergerfs/vendored/boost/exception/exception.hpp

Purpose: Core Boost.Exception type and helpers for attaching diagnostic data and enabling exception cloning/current-exception support.

Important APIs, types, and functions: `boost::exception`, `error_info<Tag,T>` specializations for throw function/file/line/column, `enable_error_info`, `enable_current_exception`, internal `refcount_ptr`, `error_info_container`, `error_info_injector<T>`, `clone_base`, `clone_impl<T>`, `copy_boost_exception`, and throw-location retrieval.

Control flow: `set_info` friend helpers mutate diagnostic fields. `enable_error_info` conditionally wraps non-Boost exception types in an injector that also derives from `boost::exception`. `enable_current_exception` wraps copyable exceptions in `clone_impl`, whose virtual `clone` copies Boost.Exception metadata and whose `rethrow` throws or calls `boost::throw_exception` when exceptions are disabled.

State and persistence behavior: `boost::exception` stores mutable ref-counted diagnostic container plus throw function/file/line/column fields. State persists with copied/cloned exception objects.

Dependencies and integration points: Depends on source location, Boost config, `<exception>`, and either `boost::shared_ptr` or `std::shared_ptr` in mini-Boost mode. Used by Boost throw/catch diagnostics.

Risks: Mutable diagnostic state inside exception objects is delicate. Refcount and clone ownership must avoid leaks/double releases. No-exception mode depends on user-provided `throw_exception`.

Test signals: Attach/retrieve throw metadata, copy and clone exceptions, rethrow with current-exception wrapper, no-exception compile path, mini-Boost shared_ptr mode, and source-location extraction.
