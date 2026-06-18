# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/audio/audio.c

Read fully: 402 lines, 9991 bytes. SHA-256 prefix: `826e71b2b01e6060`.

This is the main USB audio driver command. It discovers/configures a USB audio device, parses descriptors, selects playback/record endpoints and defaults, initializes controls, optionally opens HID volume buttons, and starts control/button/server processes.

`audio_endpoint()` parses class-specific endpoint descriptors and records capabilities such as sampling-frequency control, pitch control, and max-packet-only behavior into the alternate setting’s `Audioalt`.

`threadmain()` handles options for debug, mountpoint, srv name, device number, attachment permissions, and initial volume. It finds an audio device by class/subclass/protocol, configures it, scans descriptors via `audio_interface()`/`audio_endpoint()`, chooses endpoints, sets default 44.1 kHz or fallback 48 kHz stereo 16-bit playback/recording, unmutes playback, applies volume, and starts `controlproc`, `buttonproc`, and `serve`.

`controlproc()` serializes textual control changes from the file server/buttons into `setcontrol()` calls. `buttonproc()` reads HID button events and adjusts playback volume.

Integration: works with `audioctl.c`, `audiosub.c`, and `audiofs.c`; uses Plan 9 USB library `Dev`, `Ep`, descriptor data, and endpoint control operations.

Risk notes: the file’s opening comment says the driver needs a rewrite and may cross nil pointers. Initialization has device-specific assumptions and a record fallback path that appears to force 48 kHz when the preferred rate is unavailable.
