# sources/test-tools/strace/src/getrandom.c

Decoder for `getrandom`. It prints the buffer on successful exit using the returned byte count, the requested count, and flags from `getrandom_flags`; on failure it prints the buffer address. State is syscall phase and return value. Dependencies are buffer/string byte printers and xlat flag table. Risks are leaking large random buffers without truncation controls, output after failure, and new flags. Tests should cover successful short reads, zero length, `GRND_NONBLOCK`/`GRND_RANDOM`, bad buffers, and unknown flags.
