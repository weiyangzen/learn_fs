# sources/test-tools/strace/src/getcpu.c

Decoder for `getcpu`. It prints CPU and node output pointers on exit and the unused cache argument/address as appropriate. State is only syscall phase and tracee memory. Dependencies are integer pointer printers and generic syscall formatting. Risks include output after failure, null pointers, and historical third-argument behavior. Tests should cover successful calls with both outputs, null outputs, bad pointers, and failed calls.
