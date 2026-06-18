# sources/security-integrity/selinux/libselinux/src/compute_user.c

Purpose: Implements deprecated user-context computation through `selinuxfs/user`, returning a NULL-terminated array of possible contexts for a user and source context.

Important APIs/types/functions: `security_compute_user_raw()` performs the raw query. `security_compute_user()` translates the source context and each returned raw context. It logs a deprecation warning recommending `get_ordered_context_list()`.

Control flow: raw function formats `scon user`, writes to `/user`, reads a buffer whose first string encodes the count, then walks subsequent NUL-terminated context strings into a heap array. Public wrapper converts every returned element in place, freeing the raw entries.

State and persistence: no persistent state, but it allocates caller-owned arrays freed by `freeconary()`.

Dependencies and integration: uses callbacks logging, `freeconary()`, and SELinuxfs policy service.

Risks and test signals: response parsing assumes a count followed by contiguous NUL strings. Tests should cover malformed counts, short buffers, output conversion failure cleanup, zero contexts, and missing mount.
