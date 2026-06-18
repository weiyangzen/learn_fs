# sources/storage-engines/foundationdb/cmake/CheckForPthreads.c

## Purpose
Acts as the C source used by custom `FindThreads.cmake` to verify that `-pthread` both compiles and links.

## Important APIs, Types, and Functions
Contains `start_routine` and `main`, calling `pthread_create` and `pthread_join` against `<pthread.h>`.

## Control Flow and Integration
`FindThreads.cmake` passes this file to `try_compile` with `LINK_LIBRARIES=-pthread`. The source is not intended to execute; successful compilation/linking proves the flag is usable.

## State and Persistence
Depends on POSIX pthread headers and linker support.

## Dependencies
No persistence; compiled temporary artifacts live under CMake try-compile directories.

## Risks and Test Signals
Risks are false negatives on unusual toolchains or cross-compilation environments. Test signal is the `THREADS_HAVE_PTHREAD_ARG` result and CMake check output.
