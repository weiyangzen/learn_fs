# sources/storage-engines/wiredtiger/lang/python/run-ex_access

This shell script is a legacy runner for `examples/python/ex_access.py`. It defaults `PYTHON` to `python3`, removes and recreates `WT_TEST`, then execs Python with `LD_LIBRARY_PATH`, `DYLD_LIBRARY_PATH`, and `PYTHONPATH` set for an in-tree build.

The script's only owned persistent state is the `WT_TEST` directory it recreates. It depends on `srcdir`, shared libraries under `../../.libs`, and importable Python module files in `.` or `${srcdir}`. The main risks are destructive removal of `WT_TEST`, failure when `srcdir` is unset, and mismatch with CMake build layouts. A successful example run is the test signal.
