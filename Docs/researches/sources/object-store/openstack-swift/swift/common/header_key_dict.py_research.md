# sources/object-store/openstack-swift/swift/common/header_key_dict.py

Purpose: implements a small HTTP header dictionary that normalizes keys to title case and treats lookups as case-insensitive for Swift WSGI-string headers.

Important APIs/types/functions: `HeaderKeyDict` overrides `update`, `__getitem__`, `__setitem__`, `__contains__`, `__delitem__`, `get`, `setdefault`, and `pop`. `_title` encodes Latin-1, applies byte title-casing, and decodes back to Latin-1.

Control flow: construction updates from an optional mapping/iterable and kwargs. Setting a value title-cases the key, removes the header when value is `None`, decodes byte values as Latin-1, and stringifies other values. Reads and deletes title-case the requested key before delegating to `dict`.

State and persistence: state is the in-memory dict contents. There is no persistence.

Dependencies and integration: self-contained and used by direct-client and HTTP response handling paths that need case-insensitive header access while preserving WSGI string behavior.

Risks: unlike a full multi-dict, repeated headers collapse to one value; `__getitem__` returns `None` instead of raising `KeyError`; title-casing may not preserve original spelling such as `ETag`; all non-byte values are coerced with `str`. Tests should cover mixed-case lookup, bytes values, deletion by `None`, iterable updates, and behavior for missing keys.
