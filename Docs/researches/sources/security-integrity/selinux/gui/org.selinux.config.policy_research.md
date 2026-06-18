# sources/security-integrity/selinux/gui/org.selinux.config.policy

## Purpose

This PolicyKit policy file authorizes launching the full `system-config-selinux` GUI through pkexec.

## Behavior

It defines action `org.selinux.config.pkexec.run`, describes the need to run system-config-selinux, denies arbitrary and inactive users, requires active users to authenticate as admin, and annotates the executable path as `/usr/share/system-config-selinux/system-config-selinux.py` with GUI allowance enabled.

## State And Persistence

Installed under `share/polkit-1/actions`, it persists pkexec authorization metadata for the GUI launcher.

## Dependencies And Integration Points

It depends on PolicyKit, pkexec annotations, and the install path used by `gui/Makefile`. It integrates with desktop launchers or wrapper scripts that invoke this action.

## Risks

The DTD URL uses `PolicyKit/1/policyconfig.dtd`, while the D-Bus policy file uses `PolicyKit/Policy Configuration 1.0`; packaging should ensure the form is accepted by target PolicyKit versions. The annotated path must match installation. Allowing GUI pkexec is intentional but increases the importance of GUI input validation because the application can run privileged.

## Test Signals

Tests should verify pkexec can locate the action, prompts for admin authentication, launches the installed script, and fails cleanly if the path is absent.
