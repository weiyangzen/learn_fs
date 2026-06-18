# sources/test-tools/strace/src/fstatfs.c

Decoder for `fstatfs`. It prints fd on entry, then on successful exit fetches and prints `struct statfs` through shared statfs formatting helpers. State is syscall phase and output memory. Dependencies are fd printers and `fetch_struct_statfs`/statfs printers from the statfs subsystem. Risks are printing output after failures and architecture-specific statfs layout support. Tests should cover success, error, bad output pointer, and representative filesystem flag/type values.
