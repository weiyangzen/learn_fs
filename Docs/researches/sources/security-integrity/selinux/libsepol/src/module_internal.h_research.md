# sources/security-integrity/selinux/libsepol/src/module_internal.h

Purpose: tiny internal shim header for module package implementation. It includes the public `<sepol/module.h>` declaration set for internal source files.

Important APIs and types: no new APIs or types are defined here; all visible declarations come from `<sepol/module.h>`, including `sepol_module_package_t` and module package function prototypes.

Control flow: none.

State and persistence: none.

Dependencies and integration points: used by `module.c` to pull in module package declarations through a local internal include path. It can serve as an extension point if libsepol later needs private module-package declarations without changing every source include.

Risks: the file has no include guard, but because it only includes a public header that should have its own guard, practical risk is low. Adding private declarations here should include a guard to avoid duplicate definition issues.

Test signals: compile-only coverage is sufficient; any future additions should be validated by the source files that include this shim.
