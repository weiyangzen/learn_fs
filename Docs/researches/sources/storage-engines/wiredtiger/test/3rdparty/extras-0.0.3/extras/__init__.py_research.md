<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/extras/__init__.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/extras/__init__.py

Purpose: Small compatibility utility package exporting safe attribute probing and optional import helpers.

Important APIs/functions: `__version__ = (0, 0, 3, 'final', 0)`. `try_import(name, alternative=None, error_callback=None)` progressively imports the longest available module prefix, then walks remaining attributes, returning `alternative` on import/attribute failure. `try_imports(module_names, alternative=_RAISE_EXCEPTION, error_callback=None)` tries a list and returns the first truthy import result or raises/returns fallback. `safe_hasattr(obj, attr, _marker=object())` uses `getattr` with a marker to avoid legacy `hasattr` exception-swallowing behavior.

Control flow: `try_import` splits dotted names, retries shorter module prefixes after `ImportError`, calls `error_callback` with the last import error when final resolution fails, then walks attributes. `try_imports` loops through names and delegates to `try_import`; if no module resolves and no alternative was provided, it raises a combined `ImportError`.

State and persistence behavior: No durable persistence. It imports modules into `sys.modules` as a side effect and can trigger import-time side effects from optional dependencies.

Dependencies and integration points: Uses only `sys`. `setup.py` uses `try_import('testtools.TestCommand')` to conditionally enable a test command. Other vendored testing packages can use these helpers for optional dependency compatibility.

Risks: `try_imports` tests `if module:` rather than `is not None`, so a resolved object with false boolean value would be skipped. Attribute lookup failure after a successful module import only reports `last_error` if an earlier import error happened; otherwise callback may not receive an error. Import side effects are unavoidable.

Test signals: `extras/tests/test_extras.py` covers missing modules, submodules, object attributes, callback counts, fallback ordering, and `safe_hasattr` behavior with properties including exception propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/extras/__init__.py -->
