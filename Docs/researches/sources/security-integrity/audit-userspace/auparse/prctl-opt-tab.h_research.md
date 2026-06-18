<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/prctl-opt-tab.h -->
# sources/security-integrity/audit-userspace/auparse/prctl-opt-tab.h

## Purpose
Maps `prctl` option numbers to symbolic names for audit syscall interpretation.

## Important APIs, types, and functions
The `_S` table covers legacy options through newer controls for SVE/SME, speculation, pointer auth, tagged addresses, syscall user dispatch, scheduler core, memory deny-write-execute, memory merge, and RISC-V vector control.

## Control flow
Generated `prctl_opt_i2s` is called by `interpret.c:print_prctl_opt`; other `prctl` argument decoding uses the option value to interpret capabilities and death signals.

## State and persistence behavior
Static lookup data only.

## Dependencies and integration points
Tracks `include/uapi/linux/prctl.h`. Integrated with `print_a0` and `print_a1` syscall argument dispatch.

## Risks and test signals
Risks are rapid kernel option growth and secondary-argument context mistakes. Tests should cover known options, unknown fallback, and capability/death-signal dependent argument decoding.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/prctl-opt-tab.h -->
