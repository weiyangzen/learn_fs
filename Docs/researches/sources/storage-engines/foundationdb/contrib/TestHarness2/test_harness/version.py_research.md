# sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/version.py

Purpose: small comparable FoundationDB version object for old-binary selection and feature gating.

Important APIs/types: `Version` with `version_tuple`, `_compare`, ordered comparisons, `__hash__`, `__str__`, `of_binary`, `parse`, and `max_version`.

Control flow: parsing splits `major.minor.patch`, defaulting missing minor/patch to zero. `of_binary` expects names like `fdbserver-7.1.0`; unversioned current binary returns `max_version`.

State and persistence: none.

Dependencies and integration: used by `run.py` for trace format, TLS plugin, fault injection flag support, and old binary candidate ranges.

Risks and test signals: `fdbserver-7.1.0.exe` is not stripped here, so Windows-style names may fail outside `OldBinaries._add_file`; malformed versions raise `ValueError`. Unit tests should cover comparisons against strings and `Version`, partial versions, current binary, and hash equality.
