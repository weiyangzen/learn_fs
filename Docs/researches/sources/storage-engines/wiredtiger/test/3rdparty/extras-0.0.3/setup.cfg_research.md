<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/setup.cfg -->
# sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/setup.cfg

Purpose: Legacy test and egg-info configuration for the vendored `extras` package.

Important APIs/functions: `[test]` sets `test_module = extras.tests`, `buffer = 1`, and `catch = 1`. `[egg_info]` disables build/date/SVN version tagging.

Control flow: Consumed by setuptools/test command; no runtime flow.

State and persistence behavior: Affects test command output buffering and interrupt catching, plus generated package metadata.

Dependencies and integration points: Works with `setup.py`, especially when `testtools.TestCommand` is available and registered as the `test` command.

Risks: `setup.py test` and the `[test]` command path are deprecated in modern setuptools. `catch` semantics may differ by runner.

Test signals: Running the package's test command should discover `extras.tests`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/setup.cfg -->
