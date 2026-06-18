# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/tmp.py
# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/tmp.py

Purpose: template fragments for application-owned temporary files.

Important APIs and control flow: declares `TEMPLATETYPE_tmp_t` through `files_tmp_file`, grants manage permissions for dirs/files/links and optional socket files, creates tmp file transitions, defines read/manage/dontaudit interfaces, stream-connect support through tmp content, admin additions, and no file-context constants in this file.

State and persistence: rendered into policy module outputs; runtime effects are SELinux tmp labels and transitions.

Dependencies and integration points: uses reference-policy macros `files_tmp_file`, `files_tmp_filetrans`, `files_search_tmp`, `stream_connect_pattern`, and `admin_pattern`.

Risks and test signals: tmp access is often attack surface sensitive; stream sockets in tmp paths require careful path selection. No direct tests validate generated tmp policy.
