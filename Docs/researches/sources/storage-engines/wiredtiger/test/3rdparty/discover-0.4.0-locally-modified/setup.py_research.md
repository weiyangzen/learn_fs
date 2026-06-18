<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/discover-0.4.0-locally-modified/setup.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/discover-0.4.0-locally-modified/setup.py

Purpose: Setuptools metadata and console-entry definition for the vendored `discover` module.

Important APIs/functions: Imports `discover.__version__`, defines metadata constants, reads `README.txt` as long description, builds `params`, adds console script `discover = discover:main`, sets `test_suite = discover.collector`, and calls `setup(**params)`.

Control flow: Top-level execution reads README, imports the local module, and invokes setuptools. It has no library code beyond packaging metadata assembly.

State and persistence behavior: Packaging commands generate metadata, source distributions, installs, and console scripts. No database state.

Dependencies and integration points: Requires setuptools and the adjacent `discover.py`. The console script can run test discovery from command line; `test_suite` lets legacy `setup.py test` invoke the collector.

Risks: `open('README.txt')` is relative to the current working directory, so running setup from another directory can fail. Importing `discover` during setup executes module top-level code. Classifiers target old Python versions and may not reflect current WiredTiger test runtime.

Test signals: Packaging smoke tests include `python setup.py egg_info`, console script generation, and `setup.py test` invoking `discover.collector`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/discover-0.4.0-locally-modified/setup.py -->
