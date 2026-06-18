# sources/security-integrity/selinux/semodule-utils/semodule_expand/semodule_expand.c

Purpose: `semodule_expand` expands a base SELinux module package into a kernel binary policy file, optionally choosing policy version and assertion checking.

Important APIs and flow: options are `-V`, `-v`, `-h`, `-c version`, and `-a` to disable assertion checking. It reads a base package with `sepol_module_package_read`, calls `sepol_link_modules` on the base policy to enable optional avrules, creates an output `sepol_policydb_t`, sets `sepol_set_expand_consume_base(handle, 1)`, expands with `sepol_expand_module`, optionally applies `sepol_policydb_set_vers`, and writes with `sepol_policydb_write`.

State and persistence: persistent output is the expanded policy file; transient state includes the sepol handle, module package, policy file wrapper, and output policydb. Dependencies are libsepol module/policydb APIs and filesystem I/O. Risks: `strtol(optarg, NULL, 10)` does not reject trailing junk, output is opened with `"we"` which is glibc-specific, and disabling assertions can hide policy errors. Test signals should cover version bounds, malformed packages, assertion failures, version output, and generated policy readability by libsepol.
