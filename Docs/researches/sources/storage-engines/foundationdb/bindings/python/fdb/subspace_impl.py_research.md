# sources/storage-engines/foundationdb/bindings/python/fdb/subspace_impl.py

Purpose: This file implements the Python `Subspace` abstraction, which gives tuple-encoded namespaces a stable raw key prefix.

Important APIs and types: `Subspace` exposes `key`, `pack`, `pack_with_versionstamp`, `unpack`, `range`, `contains`, `as_foundationdb_key`, `subspace`, and `__getitem__`. It composes raw prefixes with `fdb.tuple` encoding.

Control flow: Construction packs an optional prefix tuple over a raw prefix. Indexing or `subspace` creates child subspaces by appending tuple elements. `pack` and `range` prepend `rawPrefix`; `unpack` first validates prefix containment and then decodes with `prefix_len`.

State and persistence behavior: The only state is immutable-by-convention `rawPrefix`. No database operations occur here, but generated keys are used by directory layers and user code for persistent key layout.

Dependencies and integration points: It depends on `fdb.tuple` and integrates with `impl.keyToBytes` through `as_foundationdb_key`. Directory and tester extensions use subspaces to map logical names to key ranges.

Risks: `contains` uses raw prefix matching, so callers must avoid overlapping prefixes unless intentionally modeling nested spaces. Manual raw prefixes must be valid FoundationDB keys and must match tuple encoding expectations.

Test signals: Directory extension and binding tester operations cover subspace creation, key packing/unpacking, range generation, containment, and prefix stripping.
