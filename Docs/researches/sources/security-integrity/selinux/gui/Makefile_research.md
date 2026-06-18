# sources/security-integrity/selinux/gui/Makefile

## Purpose

This Makefile builds and installs the `system-config-selinux` GUI, its policy generation GUI, Python page modules, UI files, icons, desktop files, man pages, translations, and PolicyKit launcher metadata.

## Targets And Flow

Variables define install roots such as `PREFIX`, `BINDIR`, `SHAREDIR`, `DATADIR`, `MANDIR`, and `DESKTOPDIR`. `TARGETS` lists Python pages, UI files, images, and supporting modules. `all` depends on targets plus entry scripts and delegates to `po`. `install` creates directories, installs executable scripts and wrappers, copies target resources, installs man pages including localized man pages when language directories exist, installs pixmaps and hicolor icons, installs desktop entries, installs `org.selinux.config.policy`, and delegates translation install to `po`.

`clean` delegates to `po`; `relabel` and `test` are placeholders.

## State And Persistence

Installed state spans executable commands under `bin`, shared Python/UI resources under `share/system-config-selinux`, icons and pixmaps under `share`, desktop entries, man pages, translations, and PolicyKit pkexec metadata.

## Dependencies And Integration Points

It depends on make, install utilities, the files listed in `TARGETS`, language directories, and the `po` submake. It integrates with the GUI Python modules in this subset and with PolicyKit through `org.selinux.config.policy`.

## Risks

The target list must stay synchronized with actual GUI modules and UI files. Leading `-` on `mkdir` commands can hide directory creation failures. Globbing `*.desktop` can fail or install unintended files depending on the directory contents. There is no validation of Python dependencies or UI object IDs at install time.

## Test Signals

Packaging tests should verify all target files install to expected locations, entry scripts are executable, icons and desktop files are present, translations install under `LC_MESSAGES`, and the pkexec policy path matches the installed GUI script.
