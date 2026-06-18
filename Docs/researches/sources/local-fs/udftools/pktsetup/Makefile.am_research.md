# File Research: sources/local-fs/udftools/pktsetup/Makefile.am

## Role

Automake build/install definition for pktcdvd helper tools.

## Contents

- Builds two sbin programs:
  - `pktsetup` from `pktsetup.c`
  - `pktcdvd-check` from `pktcdvd-check.c`
- Adds `pktsetup.rules` to `EXTRA_DIST`.
- If `UDEVDIR` is configured, installs `pktsetup.rules` as `80-pktsetup.rules` under `$(UDEVDIR)/rules.d`.
- Removes the installed udev rule on uninstall.

## Research Notes

This makefile wires both manual pktcdvd setup and the udev automation path.
