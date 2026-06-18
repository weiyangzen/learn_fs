# sources/security-integrity/selinux/libsepol/src/libsepol.map.in

Purpose: linker version script template for libsepol. It declares the `LIBSEPOL_1.0` symbol version and controls which libsepol functions are exported from the shared library while hiding everything else as local.

Important APIs and symbols: exports the original `LIBSEPOL_1.0` public CIL, policydb, context/bool/user/port/node/iface/InfiniBand, MLS, module package, linking/expansion, and handle/message APIs, with `local: *;` hiding non-listed symbols in that base version. Later version blocks add newer APIs: `LIBSEPOL_1.1` includes CIL compile/build/write helpers and kernel/module conversion functions such as `sepol_kernel_policydb_to_conf`; `LIBSEPOL_3.0` adds policydb optimization and AST write/setter helpers; `LIBSEPOL_3.4` adds access-vector, SID, context, and transition validation services; `LIBSEPOL_3.6` adds post-AST writing; `LIBSEPOL_3.11` adds declaration-to-CIL and neverallow checking against policydb.

Control flow: there is no runtime logic. During the build, the linker consumes this template-derived script to assign symbol visibility and version metadata to the shared object.

State and persistence: affects persistent ABI of produced `libsepol.so`. Adding, removing, or renaming entries changes what downstream binaries can link against and what versioned symbols they require; placing a symbol in the wrong version block changes ABI compatibility even if the name is exported.

Dependencies and integration points: integrated by libsepol build rules, usually after configure/meson substitution for `.map.in` templates. It must match public headers and actual compiled definitions in `src/`.

Risks: missing a new public API here causes link failures or hidden symbols despite header declarations. Exporting internal helpers by mistake expands ABI surface permanently. Removing or changing an exported symbol is ABI-breaking for existing SELinux tooling.

Test signals: shared-library build should fail on undefined exported symbols when linker checks are enabled; ABI tests should compare exported symbol lists with expected baselines; downstream smoke tests should link representative tools against the generated library.
