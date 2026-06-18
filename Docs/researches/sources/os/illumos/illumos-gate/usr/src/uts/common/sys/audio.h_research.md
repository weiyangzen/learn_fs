# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/audio.h

## Purpose

`audio.h` defines legacy audio support identifiers, channel ioctl numbers, device type enumeration, and channel information structure.

## Main Content

The header sets STREAMS/module identity strings and audio direction/sleep flags. `AUDIO_INIT()` initializes a structure to all-bits-one by byte.

Audio support ioctls include channel number/type/count and device pointer queries for AD/APM/AS devices.

`enum audio_device_type` identifies cloned channel personalities such as audio, audioctl, wavetable, MIDI, time, and user-defined device types.

`audio_channel_t` reports the owning pid, cloned channel number, device type, size of the personality-specific info structure, and a pointer to that info.

## Research Notes

This is an older audio framework ABI. It is not filesystem-related, but it does show cloned-minor device and STREAMS-module conventions used by illumos drivers.
