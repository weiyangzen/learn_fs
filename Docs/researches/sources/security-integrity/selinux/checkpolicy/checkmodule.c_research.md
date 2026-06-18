# sources/security-integrity/selinux/checkpolicy/checkmodule.c

Purpose: command-line compiler for SELinux base and policy modules.

Important APIs/functions: `read_binary_policy()` opens, stats, mmaps, initializes, reads, and MLS-checks a binary policy. `write_binary_policy()` sets policy type/version/unknown handling and writes via libsepol. `main()` parses options for binary input, CIL output, module/base type, MLS, neverallow disable, warnings-as-errors, line markers, output path, unknown handling, and module policy version.

Control flow: validates incompatible options (`-U` only base, `-b` incompatible with `-m`, `-L` requires `-C`), loads source or binary policy, checks hierarchy constraints, validates module name against output basename, expands base modules when writing binary, loads initial SIDs, then writes binary or CIL if requested.

State and dependencies: uses global `sidtab`, parser globals `mlspol`/`werror`, libsepol policydb services, mmap, basename, and filesystem output.

Risks and test signals: mmapped input is not unmapped on some error paths; option compatibility is security relevant. Build tests and fuzz object builds exercise parser/link/expand paths.
