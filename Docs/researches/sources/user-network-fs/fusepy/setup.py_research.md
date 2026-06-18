## sources/user-network-fs/fusepy/setup.py

Purpose: Packages the `fusepy` Python module for distribution with setuptools metadata.

Important APIs/types/functions: top-level `setup(...)` declares name `fusepy`, version `3.0.1`, ISC license, author/maintainer metadata, `py_modules=['fuse']`, homepage, and classifiers for POSIX/macOS/Unix and Python 2.6/Python 3. It reads `README` into `long_description`.

Control flow: the script imports `setup`, opens `README`, reads it fully, then invokes setuptools. It has no conditionals beyond setuptools behavior.

State and persistence: reading `README` is the only filesystem input. Running packaging commands creates normal setuptools build/dist/egg metadata outside this source file.

Dependencies and integration points: depends on setuptools and a repository-root `README` file. It integrates with Python packaging commands such as `sdist`, `bdist`, and installation tools.

Risks: `README` is opened by relative path, so running from another working directory can fail. Package metadata points to module `fuse`, while this researched file is `fusell.py`; the low-level file may not be packaged by this setup unless included elsewhere. Classifiers still mention Python 2.6.

Test signals: no tests. Packaging validation should run `python setup.py sdist` or modern build tooling and inspect included modules.
