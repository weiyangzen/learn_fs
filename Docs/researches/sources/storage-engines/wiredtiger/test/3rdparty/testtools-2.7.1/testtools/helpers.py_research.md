# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/helpers.py

Purpose: small generic helper functions for optional imports and collection transformations.

Important APIs, types, and functions: `try_import()` attempts dotted module/object import with fallback and optional error callback. `map_values()`, `filter_values()`, `dict_subtract()`, and `list_subtract()` operate on dictionaries and lists while preserving duplicate-list semantics for subtraction.

Control flow: `try_import()` progressively shortens dotted names until a module imports, then walks the remaining attributes in reverse. If no module or attribute can be resolved, it returns `alternative` and calls `error_callback` with the last `ImportError` when provided.

State and persistence: no persistent state. Successful imports populate `sys.modules` as normal Python imports do.

Dependencies and integration points: used by package facade, test case optional fixture support, and matchers for data-structure comparisons.

Risks and test signals: `try_import()` may hide import-time errors as optional dependency absence, depending on where `ImportError` occurs. Test signals are fallback behavior for missing modules/attributes and list subtraction with repeated elements.
