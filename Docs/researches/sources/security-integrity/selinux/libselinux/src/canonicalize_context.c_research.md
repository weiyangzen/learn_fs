# sources/security-integrity/selinux/libselinux/src/canonicalize_context.c

Purpose: Implements context canonicalization through the kernel SELinux `/context` interface, with public translated and raw variants.

Important APIs/types/functions: `security_canonicalize_context_raw()` writes a raw context to `selinux_mnt/context`, reads back the canonical value, and duplicates it. `security_canonicalize_context()` converts translated input to raw, calls raw canonicalization, then converts the output back to translated form.

Control flow: the raw path requires `selinux_mnt`, opens `context` read-write, allocates a page-sized buffer, copies input with overflow checking, writes NUL-terminated context, clears the buffer, and reads the response. If read fails with `EINVAL`, it falls back to the original context for kernels lacking the extended canonicalization interface.

State and persistence: no persistent state is changed; kernel policy is queried through a transient file descriptor.

Dependencies and integration: depends on `selinux_page_size`, `selinux_mnt`, raw/translated context conversion helpers, and `freecon()`.

Risks and test signals: page-size limits and `strlcpy` overflow are the primary input-size boundary. Tests should cover missing selinuxfs, long contexts, kernel `EINVAL` fallback, conversion failures, and successful raw/trans round trip.
