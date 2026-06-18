# sources/test-tools/strace/bundled/linux/include/uapi/linux/securebits.h

## Purpose

Defines process securebits used by capability handling and `prctl(PR_GET_SECUREBITS/PR_SET_SECUREBITS)`. strace uses these masks to decode securebit values.

## Important APIs, Types, and Dependencies

The header has no include dependencies. It defines `issecure_mask`, `SECUREBITS_DEFAULT`, paired setting and lock bits for `SECURE_NOROOT`, `SECURE_NO_SETUID_FIXUP`, `SECURE_KEEP_CAPS`, `SECURE_NO_CAP_AMBIENT_RAISE`, `SECURE_EXEC_RESTRICT_FILE`, and `SECURE_EXEC_DENY_INTERACTIVE`, plus `SECBIT_*` masks. Aggregate masks are `SECURE_ALL_BITS`, `SECURE_ALL_LOCKS`, and `SECURE_ALL_UNPRIVILEGED`.

## Control Flow, State, and Integration

No executable flow is present. Kernel credential logic uses these per-task flags to decide how UID 0, setuid transitions, ambient capability raises, and exec restrictions behave. Lock bits make corresponding settings immutable from userspace.

## Risks and Test Signals

Risks are ignoring lock-bit pairs, assuming only the older four securebits exist, and treating aggregate masks as values to set blindly. Test signals include prctl securebits decode with all `SECBIT_*` names, locked/unlocked combinations, and unknown-bit fallback.
