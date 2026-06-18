<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/setup.py -->
# sources/security-integrity/selinux/libselinux/src/setup.py

## Purpose
Python packaging script for the libselinux Python extension.

## Important APIs, Types, And Functions
Calls `distutils.core.setup()` with extension module metadata, building `selinux` from `selinuxswig_python_wrap.c` and linking against `selinux`.

## Control Flow
The script is declarative: when invoked by Python packaging tools, distutils compiles the extension from the specified source and library settings.

## State And Persistence Behavior
Writes build/install artifacts as directed by distutils; no project runtime state is touched.

## Dependencies And Integration Points
Depends on generated SWIG wrapper C source, libselinux headers/libraries, and Python distutils.

## Risks And Test Signals
Risks include deprecated distutils, missing generated wrapper, library path issues, and Python version compatibility. Build/import tests for the extension are the useful signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/setup.py -->
