# File Research: sources/virtualization/libblockdev/src/python/gi/overrides/Makefile.am

This Automake file installs Python GI overrides.

Behavior:
- Only active when `WITH_PYTHON3` is set.
- Computes `py3libdir` using `python3 -c "import sysconfig; ..."` with `platbase=${exec_prefix}`.
- Installs `BlockDev.py` into `$(py3libdir)/gi/overrides`.
- Distributes `__init__.py` as a non-installed source.
- Cleans `Makefile.in` on maintainer clean.

Research relevance:
- This is the installation hook that makes PyGObject load the `BlockDev.py` overrides automatically.
