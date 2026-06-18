# sources/test-tools/strace/src/fstatfs64.c

Decoder for `fstatfs64`. It prints fd, size, and output statfs64 structure, validating the user-supplied size through `fetch_struct_statfs64`. State is syscall phase and output memory. Dependencies are statfs64 fetch/print helpers and fd formatting. Risks are accepting or rejecting ABI-specific padded sizes, output after errors, and size argument mismatches. Tests should cover valid sizes, invalid sizes, bad pointers, compat personalities, and successful filesystem stats.
