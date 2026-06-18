# File Research: sources/os/bsd/freebsd-src/sbin/devd/snd.conf

## Purpose
Redirects virtual audio endpoints when sound devices connect or disconnect.

## Main Elements
- SND `CONN` `IN` for `dsp[0-9]+`: tells `virtual_oss_cmd` to use recording device.
- SND `CONN` `OUT`: tells `virtual_oss_cmd` to use playback device.
- SND `CONN` `NODEV`: redirects to `/dev/null` to avoid repeated errors.

## Dependencies And Integration
Uses `sysrc` to find `virtual_oss_default_control_device` and calls `virtual_oss_cmd` if present.
