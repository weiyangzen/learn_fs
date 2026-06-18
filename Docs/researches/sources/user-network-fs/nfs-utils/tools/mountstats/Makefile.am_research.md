# sources/user-network-fs/nfs-utils/tools/mountstats/Makefile.am

Purpose: `tools/mountstats/Makefile.am` packages and installs the Python `mountstats` utility and its man page.

Important build APIs and control flow: It lists `mountstats.py` as `PYTHON_FILES`, includes `mountstats.man`, makes the Python file part of `EXTRA_DIST`, and installs it executable as `$(sbindir)/mountstats` in `install-data-hook`.

State, dependencies, and integration: No build-time compilation occurs; install behavior copies the script directly. Runtime integration is with `/proc/self/mountstats`.

Risks and test signals: Install hooks must preserve executable mode and shebang compatibility. Tests should run `make install DESTDIR=...`, verify path/mode/manpage, and execute the installed script with a fixture file.
