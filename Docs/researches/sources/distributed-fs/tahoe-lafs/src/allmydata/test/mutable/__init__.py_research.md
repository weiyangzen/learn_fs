<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/__init__.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/__init__.py

Purpose: Marks `allmydata.test.mutable` as a Python package for mutable-file tests.

Important APIs and functions: No public APIs, imports, or executable definitions are present.

Control flow: No runtime control flow.

State and persistence: No state or persistence.

Dependencies and integration points: Enables relative imports among mutable test modules such as `.util`, `test_filenode`, `test_checker`, and problem/encoding tests.

Risks: Minimal; package-level side effects are intentionally absent. Adding imports here could change test discovery or introduce global setup costs.

Test signals: Importing `allmydata.test.mutable` should remain side-effect free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/__init__.py -->
