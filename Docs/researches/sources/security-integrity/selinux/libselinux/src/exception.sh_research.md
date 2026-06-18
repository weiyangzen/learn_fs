# sources/security-integrity/selinux/libselinux/src/exception.sh

Purpose: Generates SWIG Python exception wrappers for public libselinux integer-returning APIs.

Important APIs/types/functions: shell function `except()` emits a `%exception` block for most functions, translating negative `result` into `PyErr_SetFromErrno(PyExc_OSError)` and `SWIG_fail`. `selinux_file_context_cmp` is explicitly ignored.

Control flow: the script concatenates selected public headers, compiles with `${CC:-gcc}` and `-aux-info` to extract extern int function names, falls back to `gcc` if the configured compiler cannot support `-aux-info`, emits exception wrappers for each extracted function, and removes temporary files.

State and persistence: generated output is `selinuxswig_python_exception.i`; temporary `temp.aux` and `temp.o` are deleted.

Dependencies and integration: invoked by the makefile before Python wrapper builds. Depends on compiler support, public headers, Python/SWIG conventions, and shell/awk.

Risks and test signals: compiler output format changes can break function extraction. Tests should run the target with GCC and Clang fallback, verify ignored functions, and ensure temp files are removed on failure.
