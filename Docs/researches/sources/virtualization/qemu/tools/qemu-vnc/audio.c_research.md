# File Research: sources/virtualization/qemu/tools/qemu-vnc/audio.c

## Purpose
Audio support for standalone `qemu-vnc`, connecting to QEMU’s D-Bus display audio interface and exposing received audio to QEMU’s VNC audio capture path.

## Main Structures
- `CaptureVoiceOut`: registered capture consumer with audio settings and callbacks.
- `AudioOut`: currently tracked D-Bus output stream ID and audio settings.

## Behavior
- Handles D-Bus `AudioOutListener` methods: `Init`, `Fini`, `SetEnabled`, `SetVolume`, and `Write`.
- Converts D-Bus audio format metadata into QEMU `audsettings`.
- Tracks one active output stream in `audio_out`.
- On enable/disable, notifies all registered capture callbacks.
- On write, forwards raw bytes only to captures with matching format/settings.
- Provides a dummy `AudioBackend` so VNC audio capture registration has a non-NULL backend.
- Sets up a peer-to-peer D-Bus connection via socketpair and registers an audio listener with QEMU.

## Filesystem/Storage Relevance
None directly. It is part of virtualization UI/audio tooling around QEMU.

## Notable Limitations
No resampling, mixing, or format conversion is implemented; mismatched capture settings are ignored.
