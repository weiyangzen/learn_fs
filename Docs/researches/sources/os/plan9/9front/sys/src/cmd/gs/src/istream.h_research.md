# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/istream.h

Declares interpreter support procedures for streams exported by `zfproc.c`. It includes procedure stream initialization functions `sread_proc` and `swrite_proc`, plus read/write exception handlers used by the interpreter, scanner, file I/O, and painting code.

These handlers bridge stream interrupts or callbacks into the execution-stack continuation model through `op_proc_t` continuations.
