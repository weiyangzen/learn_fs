# sources/user-network-fs/mergerfs/vendored/boost/core/nvp.hpp

Purpose: Lightweight name-value-pair wrapper used by Boost serialization-facing code without depending on full Boost.Serialization.

Important APIs, types, and functions: `boost::serialization::nvp<T>`, `make_nvp(char const*, T&)`, and exposed aliases in `boost::core` through `serialization.hpp`.

Control flow: Construction stores a name pointer and value reference/pointer; archive operators can inspect name and value.

State and persistence behavior: Holds non-owning references to a name string and value. It does not serialize by itself.

Dependencies and integration points: Used by `boost/core/serialization.hpp` and code that needs a minimal archive adapter.

Risks: Name and value lifetimes must outlive the wrapper. It is a compatibility shim, not a full serialization implementation.

Test signals: Compile archive code using `make_nvp`, const/non-const values, and integration through `boost::core` aliases.
