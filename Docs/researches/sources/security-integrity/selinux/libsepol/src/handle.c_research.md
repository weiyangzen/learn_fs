# sources/security-integrity/selinux/libsepol/src/handle.c

Purpose: implements allocation, destruction, and option accessors for `sepol_handle_t`, the central libsepol object carrying diagnostics and expansion behavior flags.

Important APIs and functions: `sepol_handle_create` allocates a handle, installs `sepol_msg_default_handler`, and initializes `disable_dontaudit`, `expand_consume_base`, and `preserve_tunables` to zero. `sepol_get_preserve_tunables`/`sepol_set_preserve_tunables`, `sepol_get_disable_dontaudit`/`sepol_set_disable_dontaudit`, and `sepol_set_expand_consume_base` expose option fields. `sepol_handle_destroy` frees the handle.

Control flow: creation performs one allocation, initializes fields, and returns NULL on allocation failure. Accessors assert non-NULL handles, then read or write simple integer fields.

State and persistence behavior: no persistent storage. The handle owns only its struct memory; callback argument ownership belongs to the caller. Options persist for the life of the handle and influence later expansion/logging calls.

Dependencies and integration points: includes internal `handle.h` and `debug.h`. `expand.c` reads `disable_dontaudit`, `expand_consume_base`, and `preserve_tunables`; `debug.c` and `debug.h` use callback fields.

Risks: accessors abort on NULL because they use `assert`, which may disappear in release builds if `NDEBUG` is set. There is no getter for `expand_consume_base` in this file. Destroy does not invoke callback-argument cleanup.

Test signals: handle creation defaults, option round trips, behavior of expansion with each option, custom callback survival across handle lifecycle, NULL allocation handling, and sanitizer checks for use-after-free by callers.
