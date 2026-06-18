# sources/storage-engines/wiredtiger/test/compatibility/common/compatibility_config.py

Purpose: Centralizes branch lists and checkout-directory configuration for Python compatibility tests, importing branch policy from the shell `meta/versions.sh` file.

Important APIs/types/functions: `WTBranches` holds `SUITE_RELEASE_BRANCHES` as `WTVersion` objects. `extract_versions` reads `versions.sh`, regexes `export SUITE_RELEASE_BRANCHES="..."`, removes line continuations, splits branches, constructs `WTVersion` instances, filters invalid entries, and raises if no expected variable is found. `__bool__` validates that a usable suite branch list exists.

Control flow: at import time, `META_DIR` is derived beside the file, `BRANCHES` is populated from `versions.sh`, and `BRANCHES_DIR` is set to `COMPATIBILITY_TEST`.

State and persistence: no runtime persistence; the file maps durable branch policy in `versions.sh` into Python objects.

Dependencies/integration: depends on `compatibility_version.WTVersion` for validation/ordering and is consumed by `compatibility_common` and `compatibility_test`.

Risks and test signals: the regex is tied to exported shell variable shape and currently reads only `SUITE_RELEASE_BRANCHES`. Bad branch strings are silently filtered, but an entirely missing/empty suite list raises. Any new version-list variable needed by Python tests must be explicitly added here.
