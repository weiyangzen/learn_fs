# sources/security-integrity/selinux/restorecond/restore.c
# sources/security-integrity/selinux/restorecond/restore.c

Purpose: initializes libselinux restorecon state for restorecond.

Important APIs and control flow: `restore_init(struct restore_opts *opts)` creates a file-label handle with `selabel_open(SELABEL_CTX_FILE, ...)`, ORs selected option bitfields into `opts->restorecon_flags`, installs the handle via `selinux_restorecon_set_sehandle()`, and optionally sets an alternate root path.

State and persistence: stores the selabel handle and restore flags in `restore_opts`; no durable writes until callers invoke `selinux_restorecon()`.

Dependencies and integration points: used by `restorecond.c` before watches start. Depends on libselinux label and restorecon APIs.

Risks and test signals: exits on handle/open/rootpath failures, so daemon startup fails hard if label databases are unavailable. No direct tests cover alternate root or option composition.
