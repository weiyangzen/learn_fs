# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/audio/usb_ac/usb_ac.h

## Purpose
Private/shared header for the USB audio control driver coordinating audio-control, audio-streaming, HID controls, mixer, power management, and plumbed stream state.

## Main Interfaces
- Declares `usb_ac_open`, `usb_ac_close`, `usb_audio_attach`, `usb_ac_get_audio`, `usb_ac_send_audio`, and `usb_ac_stop_play`.
- Defines unit and plumbing structures such as `usb_ac_unit_list_t`, `usb_ac_plumbed_t`, `usb_ac_to_as_req_t`, `usb_ac_streams_info_t`, and `usb_ac_power_t`.
- Defines audio format and engine structures `usb_audio_format_t` and `usb_audio_eng_t`.
- Defines `usb_audio_ctrl_t` for mixer/control state.
- Defines central `usb_ac_state_t`/`struct usb_ac_state` with DDI/USB handles, descriptors, streams, plumbed endpoints, power state, audio control lists, format/engine data, and synchronization state.
- Defines state and flag constants for plumbed/unplumbed restore states, default open state, plumbed stream types, registration/setup, stereo control packing, and gain limits.

## Dependencies And Relationships
Includes `sys/sunldi.h`, `sys/sysmacros.h`, and `sys/usb/usba/usbai_private.h`. It works with `usb_audio.h`, `usb_as.h`, `usb_ah.h`, and `usb_mixer.h` in the USB audio client stack.

## Research Notes
This header is the integration point for USB audio control. It tracks topology units and plumbs child audio streaming/HID pieces into a single audio device view.
