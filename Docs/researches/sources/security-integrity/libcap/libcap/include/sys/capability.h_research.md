## sources/security-integrity/libcap/libcap/include/sys/capability.h

Purpose: primary public C API header for libcap capability, IAB, process, file, text, mode, prctl, UID/GID, launcher, and low-level syscall interfaces.

Important APIs/types: `cap_t`, `cap_value_t`, `cap_flag_t`, `cap_iab_vector_t`, `cap_iab_t`, `cap_flag_value_t`, `cap_mode_t`, `cap_launch_t`, `LIBCAP_MAJOR/MINOR`, and declarations for `cap_init/free/dup`, flag APIs, file APIs, proc APIs, ambient/bounding, external/text conversion, IAB APIs, `cap_set_syscall`, mode/secbits/prctl, UID/GID wrappers, launcher setters, `capget/capset`, and deprecated `capgetp/capsetp`.

Control flow: header-only declarations and constants; includes Linux UAPI capability definitions after defining `__user`.

State/persistence: no runtime state, but defines ownership contracts for opaque heap objects and process/file mutating calls.

Dependencies/integration: `<linux/capability.h>`, sys/types, stdint, C++ extern guards. Consumed by libcap clients, PAM module, C tests, and cgo.

Risks: ABI stability is critical; opaque pointers require callers to use `cap_free`; `cap_proc_root` is explicitly global and not thread-safe to write; deprecated APIs remain exposed.

Test signals: compile public examples against installed header, pkg-config include path checks, and ABI/API comparison across releases.
