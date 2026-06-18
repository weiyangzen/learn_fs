# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/etc_rw.py
# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/etc_rw.py

Purpose: template fragments for writable application configuration under `/etc`.

Important APIs and control flow: exposes string constants for type declarations (`TEMPLATETYPE_etc_rw_t` with `files_type`), management rules for directories/files/links, optional Unix socket management, interfaces for searching, reading, managing config files, stream connecting through an `/etc` socket, admin interface additions, and file-context patterns for a file or tree. There is no runtime control flow.

State and persistence: rendered into generated policy `.te`, `.if`, and `.fc` artifacts. The generated rules allow the application domain to manage matching config content and create labels through `files_etc_filetrans`.

Dependencies and integration points: depends on reference-policy macros such as `manage_dirs_pattern`, `files_etc_filetrans`, `files_search_etc`, `stream_connect_pattern`, and `admin_pattern`.

Risks and test signals: broad manage rules under `/etc` are sensitive; correctness depends on callers choosing narrow file-context regexes. `if_stream_rules` exposes socket connection permissions if included. No direct tests validate placeholder replacement or policy compile behavior.
