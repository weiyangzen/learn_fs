<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/MANIFEST.in -->
# sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/MANIFEST.in

Purpose: Declares extra non-package files included in the vendored `extras` source distribution.

Important APIs/functions: No executable APIs. It includes `LICENSE`, `Makefile`, `MANIFEST.in`, `NEWS`, `README.rst`, and `.gitignore`.

Control flow: Packaging tools read this manifest during sdist creation.

State and persistence behavior: Influences distribution contents only; no runtime state.

Dependencies and integration points: Integrated with `setup.py` and setuptools/distutils source distribution behavior.

Risks: It does not include tests explicitly, relying on package discovery in setup for Python files. Including `.gitignore` may be unnecessary but reflects upstream package contents.

Test signals: Sdist inspection should confirm these metadata/support files are present.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/MANIFEST.in -->
