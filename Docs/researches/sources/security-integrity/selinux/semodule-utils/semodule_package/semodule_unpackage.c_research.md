# sources/security-integrity/selinux/semodule-utils/semodule_package/semodule_unpackage.c

Purpose: `semodule_unpackage` extracts the policy module and optionally file contexts from a module package.

Important APIs and flow: it expects `ppfile modfile [fcfile]`. It creates a module package and policy-file wrapper, reads the package with `sepol_module_package_read`, writes the contained policy with `sepol_policydb_write(sepol_module_package_get_policy(pkg), out)`, then, if a file-contexts output path was supplied and the package has file contexts, writes `sepol_module_package_get_file_contexts(pkg)` bytes.

State and persistence: outputs are the module file and optional file-contexts file. Dependencies are libsepol module APIs and filesystem I/O. Risks: extra arguments beyond the optional third are ignored, output files are opened with plain `"w"` rather than close-on-exec variants used elsewhere, and file contexts are skipped without warning when absent. Test signals should include valid package round trip, packages without file contexts, bad package input, output write failures, and extra-argument handling.
