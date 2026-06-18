# sources/security-integrity/selinux/semodule-utils/semodule_link/semodule_link.c

Purpose: `semodule_link` links a base module package with one or more additional module packages, optionally writing the linked package.

Important APIs and flow: `load_module` allocates a `sepol_module_package_t` and `sepol_policy_file`, opens a package, reads it with `sepol_module_package_read`, and returns the package. `main` parses `-h`, `-V`, `-v`, and `-o`; it requires a base package and at least one module package, loads all inputs, calls `sepol_link_packages(NULL, base, mods, num_mods, verbose)`, and writes the base package to `-o` via `sepol_module_package_write` if requested.

State and persistence: the base package is mutated in memory by linking; persistent output exists only when `-o` is supplied. Dependencies are libsepol module APIs and filesystem I/O. Risks: the tool prints loading messages unconditionally, so stdout is noisy even without `-v`; output is optional, so a successful link can have no artifact; and `"re"`/`"we"` modes are libc-specific. Test signals should include missing module handling, bad package reads, link conflicts, no-output dry runs, and output package re-read validation.
