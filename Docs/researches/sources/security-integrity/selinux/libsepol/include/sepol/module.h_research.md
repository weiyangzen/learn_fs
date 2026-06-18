# sources/security-integrity/selinux/libsepol/include/sepol/module.h

Purpose: Declares public APIs for SELinux module packages and module link/expand operations.

Important APIs and types: Opaque `sepol_module_package_t`; create/free; getters/setters for file contexts, seusers, user_extra, netfilter contexts; policy getter; package read/write/info; `sepol_link_packages`, `sepol_link_modules`, and `sepol_expand_module`.

Control flow: Callers read packages, optionally link multiple modules into a base, expand to a kernel policydb, and write packages or policydb output.

State and persistence: Module packages own policydb plus ancillary text buffers. Writes persist to `sepol_policy_file_t`.

Dependencies and integration points: Ties public handle/policydb APIs to internal module representation and linker/expander.

Risks: Setters taking `char *data` raise ownership questions that callers must follow from implementation docs. Link/expand options can consume base policy depending on handle settings.

Test signals: Package read/write round trips, module info extraction, link failures, and expansion with assertions validate this API.
