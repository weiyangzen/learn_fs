<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/discover-0.4.0-locally-modified/setup.cfg -->
# sources/storage-engines/wiredtiger/test/3rdparty/discover-0.4.0-locally-modified/setup.cfg

Purpose: Source distribution configuration for the vendored `discover` package.

Important APIs/functions: No runtime APIs. The `[sdist]` option `force-manifest = 1` tells legacy distutils/setuptools to regenerate the manifest for source distributions.

Control flow: Packaging-time only.

State and persistence behavior: Affects generated sdist manifests, not WiredTiger runtime or test execution.

Dependencies and integration points: Read by setup tooling invoked from `setup.py`.

Risks: `force-manifest` is legacy behavior and may be ignored or deprecated by newer tooling. If ignored, stale manifest issues would need another packaging path.

Test signals: Running an sdist build should refresh included file lists.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/discover-0.4.0-locally-modified/setup.cfg -->
