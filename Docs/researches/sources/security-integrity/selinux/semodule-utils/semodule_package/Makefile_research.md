# sources/security-integrity/selinux/semodule-utils/semodule_package/Makefile

Purpose: builds and installs `semodule_package` and `semodule_unpackage`.

Important flow: install defaults and warning flags match sibling makefiles. `all` declares both tools, but only `semodule_package: semodule_package.o` is explicitly listed; `semodule_unpackage` relies on make's implicit rules. Installation writes both executables and both manpages, plus optional localized manpages. `clean` removes both binaries and objects.

State and persistence: outputs are local binaries/object files and installed files under `DESTDIR`. Dependencies are libsepol and implicit make rules. Risks: relying on implicit construction for `semodule_unpackage` can be fragile in constrained make environments, `-Werror` increases compiler-version sensitivity, and no tests are declared. Test signals should include both binary builds, DESTDIR installation, manpage presence, and clean idempotence.
