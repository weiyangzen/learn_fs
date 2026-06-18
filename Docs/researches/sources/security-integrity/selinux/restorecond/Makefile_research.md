# sources/security-integrity/selinux/restorecond/Makefile
# sources/security-integrity/selinux/restorecond/Makefile

Purpose: builds and installs the `restorecond` daemon and related service/config/autostart files.

Important APIs and control flow: defines install directories, systemd/dbus paths from `pkg-config`, GIO flags for DBus support, compiler/linker flags for libselinux and gio, object dependencies, and the `restorecond` link target. `install` installs the binary, manpage translations, init script, SELinux config files, XDG autostart desktop file, DBus service file, and system/user systemd units. `relabel` restores the installed binary context.

State and persistence: creates build objects/binary and installs under `DESTDIR` plus configured system paths.

Dependencies and integration points: depends on libselinux, gio-2.0, systemd pkg-config variables, make, compiler toolchain, and restorecond source files.

Risks and test signals: DBus support is always enabled via `-DHAVE_DBUS` if gio is present; install paths mix system and user service locations. No explicit `test` target exists in this Makefile.
