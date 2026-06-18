# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/identity_log.py

Purpose: provides thread-local identity tagging for log records. It lets ntlmrelayx code add an identity prefix to log formatting without passing identity through every logging call.

Important APIs and control flow: `_get_identity()` reads `_tlocal.identity` if set. `set_identity(identity)` updates the current thread's identity. `identity_context(identity)` saves the previous identity, sets a new one for the block, and restores the previous value in `finally`, supporting nested usage. `IdentityFilter.filter()` injects `record.identity` as either `"<identity> -> "` or an empty string and always returns `True`.

State and persistence: state is thread-local memory only. No disk or network side effects. Context restoration is explicit and exception-safe.

Dependencies and integration: depends on `logging`, `threading.local`, and `contextlib.contextmanager`. It integrates with logging configuration that includes `%(identity)s` and installs `IdentityFilter`.

Risks and test signals: identity is thread-local, so async tasks or worker pools that change threads will not inherit it automatically. Formatters expecting `identity` need the filter installed. Tests should cover default empty identity, set/read behavior, nested context restoration after normal return and exception, per-thread isolation, and `LogRecord` enrichment.
