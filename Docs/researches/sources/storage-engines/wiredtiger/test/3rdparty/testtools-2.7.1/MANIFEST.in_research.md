# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/MANIFEST.in

Purpose: source-distribution manifest for upstream `testtools`.

Important APIs, types, and functions: includes `LICENSE`, `Makefile`, `MANIFEST.in`, `NEWS`, `README.rst`, and `.gitignore`; prunes `doc/_build`.

Control flow: packaging tools read the manifest during sdist generation, add listed project files, and exclude generated documentation build output.

State and persistence: no runtime state. It affects the persistent file set in source archives.

Dependencies and integration points: integrates with `pyproject.toml`, `setup.py`, and setuptools/hatch packaging behavior.

Risks and test signals: manifest is minimal and relies on backend/package discovery for package files. Test signal is an sdist containing metadata/docs but not generated Sphinx output.
