# sources/security-integrity/selinux/checkpolicy/checkpolicy.c

Purpose: main SELinux policy compiler and optional interactive policy service debugger.

Important APIs/functions: parses source or binary policies, links optional blocks, expands modules to kernel policy, writes binary policy, CIL, or policy.conf, sorts ocontexts, optimizes kernel policy, and exposes debug menu calls into libsepol service APIs. Helpers display booleans/conditional expressions, change booleans, check MLS levels, print SIDs, and optionally identify equivalent types.

Control flow: command-line options select binary/source, debug, target platform, MLS, output format, policy version, sorting, optimization, unknown handling, neverallow checking, CIL line markers, and warnings-as-errors. Source input builds a base parse policy, validates levels, links optionals, and expands unless CIL output is requested. Binary input is mmapped and version-adjusted. Output is written before debug mode; without debug it cleans up and exits. Debug mode enters a menu loop for access-vector, SID/context, transition, filesystem, network, boolean, constraint, InfiniBand, and equivalent-type queries.

State and dependencies: global `policydb`, `sidtab`, `policydbp`, parser globals, mmap data, and interactive stdin state. Depends heavily on libsepol, parser/scanner objects, networking address parsing, and filesystem I/O.

Risks and test signals: large option surface, policy version downgrades/upgrades, MLS consistency, and interactive input parsing are risk points. Roundtrip tests, CI build variants, and fuzzing cover parse/link/expand/write conversions.
