## sources/security-integrity/audit-userspace/src/ausearch-lookup.h

Purpose: declares readable lookup and safe output helpers.

Important APIs/types: exposes AVC result/success lookup, syscall and uid lookup with buffer access annotations, UID cache cleanup, audit string `unescape()`, TTY data printing, and safe string output helpers.

Control flow/state: callers pass parsed `llist` context for syscall naming and receive pointers to caller-provided buffers or static strings. `unescape()` returns heap memory and must be freed.

Dependencies/integration: includes `libaudit.h` and `ausearch-llist.h`, connecting lookup behavior to the central event model.

Risks/test signals: callers must honor buffer sizes and ownership. Tests should verify return lifetime expectations for every lookup function and escaping mode behavior.
