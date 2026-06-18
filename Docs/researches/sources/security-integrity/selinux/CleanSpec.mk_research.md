# sources/security-integrity/selinux/CleanSpec.mk

Purpose: Android-style clean specification placeholder.

Important behavior: comments state the empty file prevents the build system from descending into subdirectories.

Control flow/state/dependencies: no executable rules, state, or dependencies.

Integration points: recognized by build systems that scan `CleanSpec.mk`; its presence is itself the behavior.

Risks and test signals: if removed, an external build system may perform unwanted recursive clean behavior. No local tests target it directly.
