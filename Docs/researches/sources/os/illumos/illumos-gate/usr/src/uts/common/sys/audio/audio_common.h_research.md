# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/audio/audio_common.h

## Purpose

`audio/audio_common.h` defines common kernel audio framework types, data formats, minor-number encoding, control IDs, port labels, common values, walk results, control types, and control flags.

## Main Content

Opaque framework types include audio parameters, buffers, streams, engines, clients, devices, mixer/engine ops, and controls. `audio_ctrl_desc_t` describes one control with name, type, flags, min/max values, and optional enum labels.

The file defines audio data format bit masks for u-law, A-law, signed/unsigned integer PCM in multiple sizes/endian forms, packed 24-bit, AC3, opaque formats, convertible formats, and PCM conversion formats. Endian macros map native/opposite-endian names.

Minor-number macros encode instance and device type for mixer, dsp, devaudio, devaudioctl, sndstat, and driver-reserved minors.

## Controls

The header standardizes many control IDs and port names, plus boolean and level strings. Control types include boolean, enum, stereo, mono, and meter. Flags describe readability, writability, VU peak, dB units, polling, volume roles, playback/record, 3D, tone, monitor, digital, and multi-select enum behavior.

## Research Notes

This is the shared vocabulary for illumos kernel audio drivers and the audio framework.
