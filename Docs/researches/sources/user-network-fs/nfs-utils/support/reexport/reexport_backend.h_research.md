# sources/user-network-fs/nfs-utils/support/reexport/reexport_backend.h

Purpose: `reexport_backend.h` defines the backend plugin interface used by `fsidd` to store and retrieve reexport path/fsid mappings.

Important APIs and types: `struct reexpdb_backend_plugin` contains `fsidnum_by_path`, `path_by_fsidnum`, `initdb`, and `destroydb` callbacks. It declares the sqlite implementation `sqlite_plug_ops`.

State, dependencies, and integration: The header itself owns no state. `fsidd.c` uses a `struct reexpdb_backend_plugin *` initialized to `&sqlite_plug_ops`, making sqlite the built-in backend.

Risks and test signals: There is no version field or capability negotiation, so new backends must preserve callback semantics exactly. Tests should compile with sqlite backend, add a mock backend in unit tests, and validate found/not-found/error separation in callback outputs.
