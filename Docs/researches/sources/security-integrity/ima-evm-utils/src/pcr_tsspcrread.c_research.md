
# sources/security-integrity/ima-evm-utils/src/pcr_tsspcrread.c

## Purpose
`pcr_tsspcrread.c` implements the `pcr.h` interface by locating and invoking the external IBM TSS `tsspcrread` command.

## Important APIs, Types, And Functions
`tpm2_pcr_supported()` uses `get_cmd_path()` to resolve `tsspcrread` into a static `path` buffer. `tpm2_pcr_read()` builds a command line with `-halg`, `-ha`, and `-ns`, reads one output line through `popen()`, converts hex to binary with `hex2bin()`, and returns command failure output through `errmsg`.

## Control Flow
Support probing must run before reads so `path` is populated. Each PCR read shells out, captures the first line, closes the process, treats short successful output as an unallocated bank, and converts the line into the requested digest length.

## State And Persistence
The static `path` buffer is process state. No disk state is modified. The external command reads TPM state.

## Dependencies And Integration Points
This backend depends on `PATH`, `tsspcrread`, shell command execution through `popen()`, `utils.c`, and libimaevm logging. It is a fallback-style integration where direct library linkage is not used.

## Risks
The command line is constructed with algorithm and PCR values controlled by program options; algorithm names are expected to be trusted internal values. Output parsing assumes one hex line and does not strongly validate exact length before `hex2bin()`. Forking for every PCR is slower than library backends.

## Test Signals
`boot_aggregate.test` and measurement verification can exercise this backend when `tsspcrread` is installed. `get_cmd_path()` behavior is independently relevant.
