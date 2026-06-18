# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/var_spool.py
# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/var_spool.py

Purpose: template fragments for queued/spooled application content.

Important APIs and control flow: declares `TEMPLATETYPE_spool_t`, grants manage access to dirs/files/links and optional sockets, creates spool file transitions, defines interfaces for search/read/manage spool files and directories, stream connect through spool sockets, admin additions, and file/directory contexts.

State and persistence: rendered policy controls durable spool queues and labels.

Dependencies and integration points: relies on `files_spool_filetrans`, `files_search_spool`, `manage_*_pattern`, `read_files_pattern`, `stream_connect_pattern`, and `admin_pattern`.

Risks and test signals: spools often cross trust boundaries between producers and consumers; manage and socket permissions can be high impact. No direct tests validate generated spool policy.
