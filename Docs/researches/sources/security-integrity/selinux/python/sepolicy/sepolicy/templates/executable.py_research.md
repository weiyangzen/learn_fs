# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/executable.py
# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/executable.py

Purpose: central policy template set for executable-backed domains and application/service variants.

Important APIs and control flow: exports many string templates rather than executable code. Type templates cover daemon, init script, DBus daemon, inetd service, user app, sandbox, and CGI/apache content module shapes. Rule fragments add common capabilities such as fifo/socket self access, DBus system bus use, syslog/audit, DNS resolution, PAM/password checks, mail, Kerberos, interactive fds, `/etc` reads, localization reads, and optional user-run integration. Interface fragments generate domain transitions, execute-in-place access, user role/run APIs, sandbox transitions, role changes, initrc transitions, DBus chat, and an admin interface assembled from begin/middle/end pieces plus optional init script support. File-context templates label executable and init-script paths.

State and persistence: no runtime state; rendered policy persists as generated `.te`, `.if`, and `.fc` files. Many generated domains start with `permissive TEMPLATETYPE_t`, so generated modules are initially permissive.

Dependencies and integration points: consumed by policy generation tooling and depends heavily on reference-policy macros (`init_daemon_domain`, `domain_entry_file`, `application_domain`, `inetd_service_domain`, `dbus_system_domain`, `domtrans_pattern`, `admin_pattern`, etc.).

Risks and test signals: generated permissive domains reduce enforcement until maintainers tighten policy. Optional fragments can grant substantial integration access, so template selection must reflect actual daemon behavior. No direct tests verify every variant; higher-level `sepolicy` CLI smoke tests only exercise generation-adjacent commands indirectly.
