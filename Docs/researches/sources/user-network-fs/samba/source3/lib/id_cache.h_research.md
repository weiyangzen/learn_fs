# sources/user-network-fs/samba/source3/lib/id_cache.h

Purpose: declares ID-cache reference parsing, deletion, and messaging registration.

Important APIs/types/functions: `struct id_cache_ref` with UID/GID/SID/username variants, `id_cache_ref_parse()`, `id_cache_delete_from_cache()`, `id_cache_register_msgs()`, and `id_cache_delete_message()`.

Control flow: consumers parse text references and delete directly or through messaging.

State/persistence behavior: API operations mutate idmap cache entries stored in gencache.

Dependencies/integration: depends on messaging and SID/idmap types.

Risks/test signals: struct layout and parser/deleter assumptions must remain aligned. Compile and idmap-cache tests are primary signals.
