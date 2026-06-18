# sources/security-integrity/selinux/semodule-utils/semodule_package/semodule_package.c

Purpose: `semodule_package` packages a binary policy module with optional file contexts, seusers, user_extra, and netfilter contexts into a libsepol module package.

Important APIs and flow: long options require `-m/--module` and `-o/--outfile`, with optional `-f`, `-s`, `-u`, and `-n`. `file_to_data` opens optional files with `O_CLOEXEC`, stats them, and mmaps non-empty content. `main` enforces single occurrence for each input option, reads the module policy through `sepol_policydb_read(sepol_module_package_get_policy(pkg), mod)`, attaches optional payloads with `sepol_module_package_set_*`, then writes the package with `sepol_module_package_write`.

State and persistence: the persistent output is the packaged `.pp`-style file; optional payloads are mapped read-only and copied into package structures by libsepol. Dependencies are libsepol module APIs, mmap, and filesystem operations. Risks: zero-length optional payloads are silently omitted, `user_extra` setter is gated by pointer presence rather than length, and the error message for write failure prints `argv[1]` instead of the output path. Test signals should cover duplicate options, missing required options, optional payload round trips, empty payload behavior, and malformed module input.
