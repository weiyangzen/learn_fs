<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/utils.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/utils.py

Purpose: Deprecated compatibility module for old `testtools.utils` imports.

Important APIs/types/functions: Emits a `DeprecationWarning` directing callers to import `iterate_tests` from `testtools.testsuite`.

Control flow: Warning is emitted at import time.

State and persistence behavior: No state.

Dependencies and integration points: Depends only on Python `warnings`; compatibility shim for older third-party code in the vendored package.

Risks and test signals: Does not re-export `iterate_tests`, so callers expecting the legacy symbol may fail. Import tests should verify warning behavior and compatibility expectations for this vendored release.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/utils.py -->
