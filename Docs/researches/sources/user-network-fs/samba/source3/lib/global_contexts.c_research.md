# sources/user-network-fs/samba/source3/lib/global_contexts.c

Purpose: lazily owns process-global tevent and messaging contexts.

Important APIs/types/functions: `global_event_context()`, `global_event_context_free()`, `global_messaging_context()`, and `global_messaging_context_free()`.

Control flow: accessors initialize singleton event and messaging contexts on first use; free functions release them.

State/persistence behavior: static process-local pointers hold singleton state. Messaging initialization may create socket/lock-directory artifacts indirectly.

Dependencies/integration: depends on tevent creation and `messaging_init()`.

Risks/test signals: lifecycle after fork, shutdown, and tests is sensitive. Tests should cover repeated access, free/recreate, and initialization failure.
