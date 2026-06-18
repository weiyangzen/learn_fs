# sources/security-integrity/selinux/libsepol/include/sepol/policydb/module.h

Purpose: Defines the internal layout of `sepol_module_package`.

Important APIs and types: `SEPOL_MODULE_PACKAGE_MAGIC`, `struct sepol_module_package` with policy pointer, package version, file_contexts, seusers, user_extra, and netfilter_contexts buffers plus lengths. Exports `sepol_module_package_init`.

Control flow: Package read/write code fills this structure; public getters/setters expose buffers through `sepol/module.h`.

State and persistence: The package owns a policydb and ancillary text buffers that are serialized into module package files.

Dependencies and integration points: Bridges public module API to internal policydb and conditional structures.

Risks: Buffer ownership and length fields must stay synchronized. Package magic/version compatibility gates read/write behavior.

Test signals: Package init/free, read/write of all ancillary sections, and version/magic validation test this structure.
