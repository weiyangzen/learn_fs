# File Research: sources/os/bsd/freebsd-src/sys/sys/ucred.h

Credential structure, external credential ABI, and credential mutation interface.

Key responsibilities:
- Defines credential flags for capability mode and group-set state.
- Defines kernel/internal `struct ucred` when `_KERNEL` or `_WANT_UCRED` is set, including reference/user counts, audit info, UID/GID sets, jail, login class, MAC label, dynamic group storage, and inline small-group storage.
- Defines external `struct xucred` and version, including compatibility union for effective group and supplementary groups.
- Defines `struct setcred`, initializer, and setcred flag bits for updating UIDs, GIDs, supplementary groups, and MAC label.
- Under `_KERNEL`, defines valid setcred mask, 32-bit compatibility records, user_setcred, batched credential reference helpers, credential copy/dup/free/COW/group/resource helpers, process credential setters, and group membership predicates.
- In userland, declares `setcred()`.

Dependencies:
- Includes `sys/types.h`, optional lock/mutex internals, and BSM audit definitions.

Notable risks:
- Comments explicitly warn not to check `cr_uid` directly for superuserness; privilege checks must go through `priv(9)`.
- `xucred` group layout carries historical ambiguity where effective GID is also first group element.
- Credential copy ranges use `cr_startcopy`/`cr_endcopy` markers and must remain synchronized with fields intended for copy-on-write duplication.
