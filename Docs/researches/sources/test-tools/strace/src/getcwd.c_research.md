# sources/test-tools/strace/src/getcwd.c

Decoder for `getcwd`. It prints the output buffer as a string on successful exit, prints the raw address on failure, and always prints the size argument. State is syscall phase and return length. Dependencies are string printers and syscall result handling. Risks are off-by-one use of returned length, non-NUL output, and output after errors. Tests should cover success, `ERANGE`, bad pointers, zero size, and paths containing unusual bytes.
