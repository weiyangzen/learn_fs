<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/extras/tests/test_extras.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/extras/tests/test_extras.py

Purpose: Unit tests for `extras.safe_hasattr`, `extras.try_import`, and `extras.try_imports`.

Important APIs/functions: `check_error_callback` is a shared assertion helper for callback behavior. `TestSafeHasattr` validates absent attributes, present attributes, properties, and property exceptions. `TestTryImport` covers missing modules, default fallback, existing modules/submodules, missing submodule attributes, object imports, and error callbacks. `TestTryImports` covers fallback sequences, combined `ImportError`, submodules, and callback counts.

Control flow: Tests use `testtools.TestCase` and matchers `Equals`, `Is`, and `Not`. The callback helper records `ImportError` instances, handles expected raised `ImportError`, and checks callback count against expectations.

State and persistence behavior: No durable state. Tests import standard-library modules such as `os` and inspect import helper behavior.

Dependencies and integration points: Depends on testtools and the local `extras` module. It is loaded by `extras.tests.test_suite`.

Risks: Tests use deprecated aliases such as `assertEquals`, which can warn or fail in future testtools/unittest versions. Negative import tests assume modules named `doesntexist` and `noreally` are absent from the environment. Callback tests expect implementation-specific callback counts.

Test signals: This file is the primary behavior specification for the `extras` package. Passing it confirms optional import fallback and safe attribute probing semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/extras/tests/test_extras.py -->
