# sources/test-tools/pynfs/nfs4.1/server41tests/st_verify.py

Purpose: `VERIFY` operation helper module with one active mandatory-attribute test and many disabled legacy cases for type, size, write-only, unsupported, and invalid UTF-8 attributes.

Important APIs/types/functions: helpers `_try_mand`, `_try_type`, `_try_changed_size`, `_try_write_only`, `_try_unsupported`; active test `testMandFile`. The helper code uses `do_getattrdict`, `use_obj`, `verify`, and supported-attribute discovery.

Control flow: `_try_mand` gathers all mandatory attributes except `rdattr_error`, issues `GETATTR`, then verifies the same attributes and reuses the object path. Disabled helpers would verify types, deliberately changed sizes, write-only attributes, and unsupported attributes.

State and persistence behavior: active code is read-only. It validates attribute comparison semantics against the current server view of a file.

Dependencies/integration: depends on `env.attr_info`, configured `usefile`, and the environment's attribute metadata. Some helper code references legacy `env.c1` methods rather than session-based helpers.

Risks and test signals: only `testMandFile` is active; most broader VERIFY coverage is commented out. The active signal is strong for mandatory-attribute round-trip consistency but narrow.
