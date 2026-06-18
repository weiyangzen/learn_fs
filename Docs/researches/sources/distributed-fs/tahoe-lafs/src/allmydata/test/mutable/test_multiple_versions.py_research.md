<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_multiple_versions.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_multiple_versions.py

Purpose: Tests mutable-file behavior when the grid contains a mix of recoverable and unrecoverable versions.

Important APIs and functions: `MultipleVersions` inherits `PublishMixin` and `CheckerMixin`. It uses `_set_versions`, `download_best_version`, `get_servermap`, `check`, `modify`, `Monitor`, `MODE_READ`, and `MODE_CHECK`.

Control flow: `setUp` publishes multiple prepared versions. `test_multiple_versions` rewrites selected shares to older/newer versions, verifies best-version download, checker badness, unrecoverable newer version reporting, merge-needed detection for parallel recoverable versions, and acceptable download from either parallel version. `test_replace` modifies a mixed-version file and verifies a new highest sequence replaces outliers.

State and persistence: Uses fake share state created by `PublishMixin`; `_set_versions` mutates share contents by index. Servermap state is rebuilt from fake storage.

Dependencies and integration points: Exercises mutable servermap health classification, checker reporting, downloader version selection, and publisher replacement logic.

Risks: Version numbering in comments and indexes can be confusing: fixture indexes map to sequence numbers indirectly. Tests assume query ordering that reveals single-share unrecoverable versions.

Test signals: Latest recoverable version is downloaded, mixed versions are reported unhealthy, one newer unrecoverable share is tracked as `(1,3)` health without merge need, parallel recoverable versions set `needs_merge`, and modify produces one clean recoverable version at the expected highest sequence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_multiple_versions.py -->
