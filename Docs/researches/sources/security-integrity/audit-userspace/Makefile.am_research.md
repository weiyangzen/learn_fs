## sources/security-integrity/audit-userspace/Makefile.am

Purpose: top-level Automake layout for audit-userspace.

It orders subdirectories for common libraries, libaudit, auparse, dispatcher, plugins, tools, bindings, docs, and rules, lists distribution extras, and defines cleanup for generated artifacts. State is build-system metadata. Dependencies are all submodule Makefile fragments. Risks are subdir order coupling because dispatcher plugins depend on libraries built earlier. Test signal is full `make` and `make distcheck`.
