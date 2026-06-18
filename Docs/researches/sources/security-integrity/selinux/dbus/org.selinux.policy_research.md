# sources/security-integrity/selinux/dbus/org.selinux.policy

## Purpose

This PolicyKit policy file defines authorization actions for the privileged `org.selinux` D-Bus API.

## Actions

It defines actions for `org.selinux.restorecon`, `org.selinux.setenforce`, `org.selinux.semanage`, `org.selinux.customized`, `org.selinux.semodule_list`, `org.selinux.relabel_on_boot`, `org.selinux.change_default_policy`, and `org.selinux.change_default_mode`. Defaults deny inactive and arbitrary users, while active sessions require `auth_admin_keep`.

## State And Persistence

Installed under `share/polkit-1/actions`, this file persists authorization defaults for PolicyKit. It does not perform actions itself; `selinux_server.py` asks PolicyKit to evaluate these action IDs.

## Dependencies And Integration Points

It depends on PolicyKit policyconfig syntax and action ID consistency with `selinux_server.py`. It integrates with D-Bus service methods and desktop authentication agents.

## Risks

All actions use broad descriptions such as "SELinux write access" or "SELinux Read access", which may not give users precise prompts. Read actions also require admin authentication, which is conservative but may reduce usability. A typo in an action ID would cause authorization failure or mismatched privilege behavior.

## Test Signals

Tests should verify every action ID used by the server exists here, default authorization results match expectations for active/inactive sessions, and prompted admin authentication allows the corresponding method.
