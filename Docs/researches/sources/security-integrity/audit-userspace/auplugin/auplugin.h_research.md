<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/auplugin.h -->
# sources/security-integrity/audit-userspace/auplugin/auplugin.h

Purpose: installed public C API for audit plugin helper library.

Important APIs and types: defines `MAX_AUDIT_EVENT_FRAME_SIZE`, opaque `auplugin_fgets_state_t`, `enum auplugin_mem`, queue flag constants, callback typedefs, global and reentrant `auplugin_fgets` APIs, `auplugin_setvbuf`, plugin lifecycle functions, event loop/feed functions, stats registration/reporting, and queue metric accessors. Attribute fallbacks keep headers usable across compilers.

Control flow and state: header only; runtime state is in `auplugin.c` and `auplugin-fgets.c`. API design exposes one global fgets instance and explicit reentrant state instances.

Dependencies and integration: includes `libaudit.h` and `auparse.h`, making plugin users compile against both audit message constants and parser callback types.

Risks and test signals: public ABI risk from enum/function changes, buffer-size contract changes, and ownership semantics for `auplugin_setvbuf_r`. Tests compile against this header and validate exported functions, but broader ABI compatibility is build/package policy.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/auplugin.h -->
