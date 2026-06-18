# sources/security-integrity/selinux/libselinux/src/label_backends_android.c

Purpose: Implements Android property and service label backends for `selabel_open()`.

Important APIs/types/functions: `selabel_property_init()` and `selabel_service_init()` share parsing/init/close/stats code but install different lookup functions. `spec_t` pairs a property/service key with a lookup record. `cmp()` sorts wildcard entries after concrete entries and longer keys first.

Control flow: init requires `SELABEL_OPT_PATH`, opens a regular file, makes two passes to count then populate specs, validates contexts if requested, checks duplicate keys, sorts specs, records digest, and installs lookup callbacks. Property lookup performs prefix match or `*`; service lookup performs exact match or `*`.

State and persistence: backend handle owns a sorted spec array and raw/translated contexts. Digest state is stored in the parent handle.

Dependencies and integration: Android builds enable these backends through makefile flags; frontend validation and translation are handled by `label.c`.

Risks and test signals: wildcard and prefix ordering are security-sensitive. Duplicate different-context keys are errors. Tests should cover property longest-prefix behavior, service exact behavior, wildcard fallback, duplicate detection, invalid context validation, empty files, and digest generation.
