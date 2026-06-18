# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/var_cache.py
# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/var_cache.py

Purpose: template fragments for application cache content under `/var/cache` or equivalent var paths.

Important APIs and control flow: declares `TEMPLATETYPE_cache_t`, grants manage access to dirs/files/links and optional socket files, creates file transitions with `files_var_filetrans`, defines interfaces for searching, reading, managing cache files/dirs, stream connecting via cache sockets, admin additions, and file-context templates for files and directory trees.

State and persistence: rendered into generated policy and file contexts.

Dependencies and integration points: depends on `files_search_var`, `files_var_filetrans`, `manage_*_pattern`, `read_files_pattern`, `stream_connect_pattern`, and `admin_pattern`.

Risks and test signals: cache directories can contain attacker-controlled content; generated manage and socket-connect permissions should be scoped by narrow file-context patterns. No direct tests cover generated cache policy.
