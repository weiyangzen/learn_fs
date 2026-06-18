# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/var_lib.py
# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/var_lib.py

Purpose: template fragments for application state/data under `/var/lib`.

Important APIs and control flow: declares `TEMPLATETYPE_var_lib_t`, grants management of dirs/files/links and optional sockets, creates `/var/lib` file transitions, defines search/read/manage file and directory interfaces, stream connect, admin additions, and file/socket/directory file contexts.

State and persistence: rendered policy governs persistent application state labels and access.

Dependencies and integration points: relies on `files_var_lib_filetrans`, `files_search_var_lib`, `manage_*_pattern`, `read_files_pattern`, `stream_connect_pattern`, and `admin_pattern`.

Risks and test signals: `/var/lib` often holds durable sensitive state, so broad manage rules require precise file-context regexes. No direct tests validate rendered state policy.
