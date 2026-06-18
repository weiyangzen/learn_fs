<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/concurrencytest-0.1.2-locally-modified/setup.cfg -->
# sources/storage-engines/wiredtiger/test/3rdparty/concurrencytest-0.1.2-locally-modified/setup.cfg

Purpose: Setuptools egg-info configuration for the vendored `concurrencytest` package.

Important APIs/types/functions: No executable APIs. The `[egg_info]` section clears `tag_build` and disables date and SVN revision tags with `tag_date = 0` and `tag_svn_revision = 0`.

Control flow: Consumed by setuptools during metadata generation; it has no runtime control flow.

State and persistence behavior: Affects generated package metadata file names and version tags during build/sdist/egg-info operations. It does not affect WiredTiger runtime state.

Dependencies and integration points: Used by `setup.py` and setuptools. It keeps vendored package metadata stable inside the WiredTiger third-party test tree.

Risks: Legacy `tag_svn_revision` is obsolete in modern setuptools but harmless. Metadata-only changes can still affect reproducible packaging if defaults change upstream.

Test signals: Build or `python setup.py egg_info` should produce untagged version metadata.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/concurrencytest-0.1.2-locally-modified/setup.cfg -->
