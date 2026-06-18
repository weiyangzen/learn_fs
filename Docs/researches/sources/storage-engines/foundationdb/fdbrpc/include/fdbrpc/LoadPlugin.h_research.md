## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/LoadPlugin.h

Purpose: Provides a small templated helper for dynamically loading fdbrpc/Flow plugin objects from shared libraries.

Important APIs/types/functions: `loadPlugin<T>(std::string const& plugin_name)` calls `loadLibrary()`, looks up a `get_plugin` symbol, and asks that symbol for `T::get_plugin_type_name_and_version()`. It returns a `Reference<T>` around the resulting pointer or a null reference.

Control flow: Loading is synchronous and linear: open library, load symbol, call symbol if present, wrap pointer. There is no retry or error detail propagation.

State and persistence behavior: The loaded library handle is not stored by this function; lifetime is delegated to `loadLibrary` implementation and the returned reference-counted plugin object. No durable state is changed.

Dependencies and integration points: Depends on Flow dynamic library helpers and `Reference<T>`. Plugin implementations must export `get_plugin` and support type-name/version negotiation.

Risks: Failure modes collapse to null, so callers must check the returned reference. ABI/version mismatches are pushed into the plugin symbol contract. Library unloading/lifetime is opaque here, so plugin objects must remain valid after `loadPlugin` returns.

Test signals: Tests should cover missing library, missing `get_plugin`, wrong plugin type/version, and a successful plugin returning a reference-counted object.
