# sources/security-integrity/selinux/python/sepolicy/sepolicy/sedbus.py
# sources/security-integrity/selinux/python/sepolicy/sepolicy/sedbus.py

Purpose: thin Python DBus proxy for the system SELinux DBus service at bus name `org.selinux` and object path `/org/selinux/object`.

Important APIs and control flow: `SELinuxDBus.__init__()` opens a system bus and stores a remote object. Methods `semanage()`, `restorecon()`, `setenforce()`, `customized()`, `semodule_list()`, `relabel_on_boot()`, `change_default_mode()`, and `change_default_policy()` forward calls to the `org.selinux` DBus interface and return remote results. The `__main__` block is a small manual probe that calls `setenforce(int(sys.argv[1]))` and prints DBus exceptions.

State and persistence: no local persistence; effects are whatever the DBus service performs, including policy customization, enforcement changes, relabel flags, and default config changes.

Dependencies and integration points: depends on `dbus`, `dbus.service`, `dbus.mainloop.glib`, and an installed SELinux DBus service. It is a client helper for GUI or management tools that need privileged operations through DBus.

Risks and test signals: no argument validation or timeout handling; DBus service availability and authorization failures propagate as exceptions. No local tests target this file.
