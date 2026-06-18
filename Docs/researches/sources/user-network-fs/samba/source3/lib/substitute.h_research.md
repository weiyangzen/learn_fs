## sources/user-network-fs/samba/source3/lib/substitute.h

Purpose: public interface for Samba substitution state and expansion functions. It declares setters/getters for process connection identity and the talloc-returning expansion functions used by configuration and service code.

Important APIs: `set_remote_proto`, `set_local_machine_name`, `get_local_machine_name`, `set_remote_machine_name`, `get_remote_machine_name`, `sub_set_socket_ids`, `set_current_user_info`, `get_current_username`, `get_current_user_info_domain`, `standard_sub_basic`, `talloc_sub_basic`, `talloc_sub_specified`, `talloc_sub_advanced`, and `talloc_sub_full`.

Control flow contract: callers first seed runtime context such as machine names, socket addresses, and user info, then call a substitution helper matching their context. `standard_sub_basic` mutates a caller buffer, while all `talloc_sub_*` APIs return allocated strings and must be freed through talloc context lifetime.

State and persistence: the state lives in the implementation as process globals; the header does not expose storage. Dependencies are Samba base types, `TALLOC_CTX`, and UID/GID types.

Risks and test signals: header users must choose the right expansion layer because basic, specified, advanced, and full token sets differ. Callers must not assume thread isolation. Tests should verify API-level ownership, permanent machine-name semantics, and that buffer-based `standard_sub_basic` truncation is acceptable for callers.
