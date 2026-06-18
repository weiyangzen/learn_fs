## sources/security-integrity/libcap/libcap/include/uapi/linux/securebits.h

Purpose: bundled Linux securebits constants that control root privilege semantics, setuid fixup, keepcaps, and ambient capability raising.

Important APIs/constants: `issecure_mask`, `SECUREBITS_DEFAULT`, `SECURE_NOROOT`, `SECBIT_NOROOT`, `SECURE_NO_SETUID_FIXUP`, `SECBIT_NO_SETUID_FIXUP`, `SECURE_KEEP_CAPS`, `SECBIT_KEEP_CAPS`, `SECURE_NO_CAP_AMBIENT_RAISE`, `SECBIT_NO_CAP_AMBIENT_RAISE`, `SECURE_ALL_BITS`, and `SECURE_ALL_LOCKS`.

Control flow: header definitions only.

State/persistence: defines bit layout passed to `PR_SET_SECUREBITS` and read from `PR_GET_SECUREBITS`.

Dependencies/integration: included via `sys/securebits.h` and used by `cap_proc.c` mode logic.

Risks: incorrect bit positions would be catastrophic for privilege behavior; comments describe security semantics and must stay aligned with kernel.

Test signals: `cap_set_mode`/`cap_get_mode` tests, `b215283.go`, and direct securebits set/get checks.
