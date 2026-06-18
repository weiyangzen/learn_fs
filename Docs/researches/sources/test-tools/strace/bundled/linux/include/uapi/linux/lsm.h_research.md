# sources/test-tools/strace/bundled/linux/include/uapi/linux/lsm.h

Purpose: defines the generic Linux Security Module userspace context ABI used by LSM-related syscalls and interfaces.

Important APIs/types/functions: `struct lsm_ctx` carries an LSM ID, LSM-specific flags, total record length, context length, and flexible `ctx` bytes. Constants identify LSMs (`LSM_ID_SELINUX`, `LSM_ID_APPARMOR`, `LSM_ID_LANDLOCK`, and others), context attributes (`LSM_ATTR_CURRENT`, `EXEC`, `FSCREATE`, `KEYCREATE`, `PREV`, `SOCKCREATE`), and `LSM_FLAG_SINGLE`.

Control flow: callers request or set security contexts by attribute and receive one or more length-delimited `lsm_ctx` records. Consumers advance through buffers using the `len` field.

State/persistence behavior: context reads are observational; context-setting APIs can mutate process security state for supported LSM attributes. Records may contain strings or binary data and must preserve NUL termination rules when string-based.

Dependencies/integration: includes `linux/stddef.h`, `linux/types.h`, and `linux/unistd.h`. Integrates with SELinux, Smack, AppArmor, Landlock, IMA/EVM, and other LSMs.

Risks and test signals: flexible arrays and counted-by metadata require robust length validation. Tests should cover multi-record buffers, unknown LSM IDs, `LSM_FLAG_SINGLE`, binary contexts, and string context length including NUL.
