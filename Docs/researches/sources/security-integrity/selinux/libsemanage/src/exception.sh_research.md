# sources/security-integrity/selinux/libsemanage/src/exception.sh

Purpose: generates SWIG Python exception wrappers for libsemanage functions that return negative integer error codes.

Important APIs/functions: shell function `except` emits a `%exception` block; the script compiles `../include/semanage/semanage.h` with `-aux-info`, falls back from `$CC` to `gcc`, extracts `extern int` function names with awk, emits wrappers, and removes temporary files.

Control flow: `src/Makefile` runs this script to produce `semanageswig_python_exception.i`. Each discovered integer-returning function gets a wrapper that checks `result < 0`, raises `PyErr_SetFromErrno(PyExc_OSError)`, and calls `SWIG_fail`.

State and persistence behavior: writes generated SWIG interface text to stdout and temporary `temp.o`/`temp.aux` files in the working directory, then deletes them.

Dependencies and integration points: depends on a compiler supporting GCC `-aux-info` or fallback gcc, public umbrella header completeness, awk, shell, Python/SWIG generated bindings.

Risks: clang fallback depends on gcc availability; parsing compiler aux output is fragile and may miss or mis-handle signatures. Test signals include generated exception file containing all public `extern int` APIs and successful SWIG Python build.
