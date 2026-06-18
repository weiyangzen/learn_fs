# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/rw.py
# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/rw.py

Purpose: generic read/write private file template for application-controlled content not tied to a standard filesystem area.

Important APIs and control flow: declares `TEMPLATETYPE_rw_t`, grants the application domain manage access to dirs/files/links and optional socket files, defines interfaces for search/read/manage files and dirs plus stream connect, and emits file-context templates for file, socket file, and directory trees.

State and persistence: rendered into generated policy and file-context files.

Dependencies and integration points: uses reference-policy helpers such as `files_type`, `manage_*_pattern`, `read_files_pattern`, `stream_connect_pattern`, and `admin_pattern`.

Risks and test signals: `fc_sock_file` labels sockets with `TEMPLATETYPE_etc_rw_t`, which differs from the module's `TEMPLATETYPE_rw_t` and may be intentional cross-template reuse or a stale copy/paste risk. Admin rules call `files_search_etc($1)` despite a generic rw type, another likely integration assumption that should be checked when rendering. No direct tests cover this mismatch.
