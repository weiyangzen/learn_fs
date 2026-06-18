# File Research: sources/virtualization/nbd/systemd/Makefile.am

## Purpose
Defines Automake rules for generating the `nbd@.service` systemd unit from shell/template fragments.

## Main Contents
- Declares `nbd@.service` as `noinst_DATA`.
- Removes generated service files on distclean.
- Distributes `nbd@.service.tmpl` and `sh.tmpl`.
- Builds `nbd@.service` by running generated `nbd@.service.sh`.
- Builds `nbd@.service.sh.in` by concatenating shell and service templates and appending `EOF`.

## Risks and Notes
The `SYSTEMD` installation stanza is commented out, so this Makefile generates but does not install the unit through the shown rules.
