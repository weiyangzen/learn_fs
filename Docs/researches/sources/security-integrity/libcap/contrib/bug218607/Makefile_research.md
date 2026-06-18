<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug218607/Makefile -->
# sources/security-integrity/libcap/contrib/bug218607/Makefile

## Purpose
Build and test makefile for bug218607, a C++/pthread repro verifying libpsx process-wide syscall behavior.

## Important APIs, Types, And Functions
Targets `all`, `test`, `threadcpp`, `../../libcap/libpsx.so`, and `clean`. Links with `-lpsx`, `-lpthread`, and an rpath to the in-tree libcap directory.

## Control Flow
Builds `libpsx.so` if needed, compiles `thread.cpp`, and `test` runs the resulting binary.

## State And Persistence Behavior
Creates `threadcpp`; clean removes it.

## Dependencies And Integration Points
Depends on g++, pthreads, in-tree libpsx, and `Make.Rules`.

## Risks And Edge Cases
The binary only runs from this directory because of the relative rpath.

## Test Signals
Signals are `threadcpp` printing PASSED and returning 0.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug218607/Makefile -->
