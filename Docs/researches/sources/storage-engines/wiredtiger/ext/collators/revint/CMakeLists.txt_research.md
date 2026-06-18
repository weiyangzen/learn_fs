# sources/storage-engines/wiredtiger/ext/collators/revint/CMakeLists.txt

Purpose: builds the reverse-integer collator extension as a loadable module.

Important APIs and control flow: sets `sources` to `revint_collator.c`, creates `wiredtiger_revint_collator` as a `MODULE` library, adds private include paths for source and generated headers/config, and applies `${COMPILER_DIAGNOSTIC_C_FLAGS}`.

State and persistence: no runtime state; produces a module artifact.

Dependencies and integration: depends on build-generated WiredTiger headers and is listed by the top-level extension umbrella as `wiredtiger_reverse_int_collator`, which should be checked for consistency with this target name.

Risks: there is a target-name mismatch risk: this file defines `wiredtiger_revint_collator`, while the top-level umbrella list references `wiredtiger_reverse_int_collator`. If no alias exists elsewhere, the umbrella target will not depend on this module.

Test signals: direct target build should compile the module; umbrella target membership should be verified by inspecting CMake targets or building `wiredtiger_ext`.
