# sources/security-integrity/selinux/libselinux/src/compute_av.c

Purpose: Computes SELinux access vector decisions by querying the kernel policy through `selinuxfs/access`.

Important APIs/types/functions: exports `security_compute_av_flags_raw()`, `security_compute_av_raw()`, `security_compute_av_flags()`, and `security_compute_av()`. The flags variants preserve `avd->flags`; compatibility variants omit flags from public result copying.

Control flow: raw computation opens `/access`, formats `scon tcon class requested` using `unmap_class()` and `unmap_perm()`, writes the request, reads a response containing allowed/decided/auditallow/auditdeny/seqno/optional flags, then maps returned decision permissions back to userspace if a kernel class mapping existed. Public wrappers translate contexts to raw before raw query and free conversions afterward.

State and persistence: read-only kernel policy query; no cache is maintained here.

Dependencies and integration: AVC calls `security_compute_av_flags_raw()` on cache misses. Class and permission mapping come from `mapping.h`.

Risks and test signals: page-buffer formatting can overflow, parse may return older five-field responses, and class mapping of unknown userspace classes is subtle. Tests should cover flags presence/absence, unknown class behavior, mapping round trips, long contexts, and kernel read/write failure.
