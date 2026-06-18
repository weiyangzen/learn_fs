# sources/user-network-fs/nfs-utils/tools/nfs-iostat/Makefile.am

Purpose: `tools/nfs-iostat/Makefile.am` packages and installs the Python NFS iostat utility.

Important build APIs and control flow: It lists `nfs-iostat.py` as the Python source, `nfsiostat.man` as the man page, includes both in distribution, and installs the script executable as `$(sbindir)/nfsiostat`.

State, dependencies, and integration: There is no compilation state. Runtime behavior belongs to the installed Python script, which is expected to inspect NFS mount statistics.

Risks and test signals: The installed command name differs from the source directory and script name, so packaging checks must verify `nfsiostat` exists and is executable. Tests should install to DESTDIR, inspect file mode/man page, and run a fixture-based smoke test.
