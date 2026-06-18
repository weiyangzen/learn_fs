# sources/user-network-fs/samba/source3/lib/global_contexts.h

Purpose: declares accessors and free functions for source3 global event and messaging contexts.

Important APIs/types/functions: forward declarations plus `global_event_context[_free]()` and `global_messaging_context[_free]()`.

Control flow: no runtime flow; callers use it to retrieve default contexts.

State/persistence behavior: returned pointers are singleton process-local objects owned by the module.

Dependencies/integration: included by modules that do not pass explicit contexts.

Risks/test signals: callers must not free returned contexts directly. Compile and lifecycle tests validate usage.
