# File Research: sources/os/bsd/freebsd-src/sbin/veriexec/veriexec.c

## Purpose
Main `veriexec` utility for querying/modifying Veriexec state, checking path status, and loading signed manifests.

## Main Elements
- Opens `_PATH_DEV_VERIEXEC` for ioctls.
- `veriexec_load()` verifies a signed manifest via `verify_signed()`, opens verified content for the lexer, and runs `yyparse()`.
- `veriexec_state_query()` maps partial state names to query bits: active, enforce, loaded, locked.
- `veriexec_state_modify()` maps state commands to Veriexec ioctls: active, enforce, getstate, lock.
- Optional `veriexec_check_labels()` prints labels for paths when label support is compiled in.
- `veriexec_check_paths()` exits nonzero when any path fails Veriexec checking.
- `main()` handles `-C`, `-h`, `-i`, optional `-l`, `-S`, `-v`, `-x`, and `-z`.
- `-z debug` supports `off` or numeric mac_veriexec debug level.
- Initializes the trust store with `ve_trust_init()` before manifest loading.

## Dependencies And Integration
Uses `/dev/veriexec`, libveriexec, libsecureboot, syslog, optional Veriexec version ioctl, and the generated manifest parser.

## Risk Notes
Manifests must verify before parsing. State-command matching uses prefix comparisons, so ambiguous prefixes are rejected only when multiple bits are set in query mode.
