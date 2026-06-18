# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/var_run.py
# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/var_run.py

Purpose: template fragments for runtime PID/socket content under `/run` or `/var/run`.

Important APIs and control flow: declares `TEMPLATETYPE_var_run_t` as `files_pid_file`, grants manage access and `files_pid_filetrans`, adds socket file transition support, defines a read-PID-files interface, a stream-connect interface, admin additions, and file/socket/directory contexts.

State and persistence: rendered policy affects runtime, non-durable PID/socket labeling and access.

Dependencies and integration points: uses `files_search_pids`, `files_pid_filetrans`, `stream_connect_pattern`, and `admin_pattern`.

Risks and test signals: socket file handling uses `manage_files_pattern` rather than `manage_sock_files_pattern` in `te_stream_rules`, which may be intentional macro compatibility or a bug to check. Stream-connect permissions on runtime sockets must be narrowly exposed. No direct tests cover this.
