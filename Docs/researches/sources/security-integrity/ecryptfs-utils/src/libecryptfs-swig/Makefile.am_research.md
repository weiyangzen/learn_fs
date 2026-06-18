# sources/security-integrity/ecryptfs-utils/src/libecryptfs-swig/Makefile.am

Purpose: conditionally builds Python SWIG bindings for libecryptfs.

Important APIs/targets: under `BUILD_PYWRAP`, generates `libecryptfs_wrap.c` from `libecryptfs.i`, installs `libecryptfs.py`, builds `_libecryptfs.la`, includes SWIG Python CPP flags and ecryptfs headers, and links against built `libecryptfs.la`.

Control flow/state: SWIG generation is a build step; wrapper C is a built source.

Dependencies/integration: configure must find Python and SWIG; Python package imports `_libecryptfs`.

Risks: Python 2-era build macros and generated wrapper may not work on modern Python. Direct link path to `../libecryptfs/.libs/libecryptfs.la` is build-tree specific.

Test signals: Python wrapper build/import and calling exposed functions.
