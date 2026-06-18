# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/soundcard.h

## Role

Compatibility shim for OSS-style soundcard interfaces.

## Key Contents

Includes `<sys/audio/audio_oss.h>` and defines no additional symbols.

## Design Notes

This header exists so consumers including `<sys/soundcard.h>` receive the illumos OSS audio compatibility definitions.
