# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/audio/audioctl.c

Read fully: 697 lines, 17862 bytes. SHA-256 prefix: `65190a43b7902f31`.

This file implements USB audio control state, alternate-setting selection, speed management, feature-unit get/set operations, and text parsing/formatting for control values.

Global arrays track endpoint IDs, interface IDs, feature/selector/mixer units, current alternate settings, and `Audiocontrol` descriptors for playback/record. `findalt()` scans endpoint alternate settings populated by descriptor parsing to find channel/resolution/speed-compatible modes while updating min/max control ranges.

`setspeed()` clamps or selects continuous/discrete/one-frequency rates, optionally sends class endpoint `SET_CUR` sampling-frequency requests, verifies current speed, opens endpoint devices, and configures endpoint polling interval, sample size, and Hz. `setcontrol()` handles logical controls: speed, channels, resolution, feature-unit controls, and selector controls.

`getspecialcontrol()`, `getcontrol()`, and `getcontrols()` query current/min/max/resolution via USB class requests and populate cached values. `ctlparse()` parses scalar or per-channel values, including percentages mapped into min/max ranges. `Aconv()` formats controls for textual output.

Integration: called by `audio.c` initialization, `controlproc`, and `audiofs.c` reads/writes. It issues `usbcmd()` and endpoint `devctl()` operations.

Risk notes: many paths return `Undef` as an error/sentinel mixed with integer values. Channel bitmaps assume up to 7 numbered channels plus master. Device quirks are handled inline, such as Griffin iMic speed reporting.
