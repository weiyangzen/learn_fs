# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/hid/hid.h

## Purpose
USB HID descriptor, request, report, protocol, event, and ioctl definitions.

## Main Interfaces
- Defines HID descriptor type and descriptor size constants.
- Defines HID class requests `HID_GET_REPORT`, `HID_GET_IDLE`, `HID_GET_PROTOCOL`, `HID_SET_REPORT`, `HID_SET_IDLE`, and `HID_SET_PROTOCOL`.
- Defines `usb_hid_descr_t` for HID class descriptors.
- Defines `hid_vid_pid_t` and `hid_req_t`.
- Defines maximum report data size and report type constants for input, output, and feature reports.
- Defines idle/protocol request lengths and boot/report protocol values.
- Defines control/event values such as `HID_GET_PARSER_HANDLE`, `HID_GET_VID_PID`, `HID_POWER_OFF`, `HID_FULL_POWER`, `HID_DISCONNECT_EVENT`, and `HID_CONNECT_EVENT`.
- Defines report descriptor type, HID version, ioctl base `HIDIOC`, and direct keyboard/mouse ioctls.

## Dependencies And Relationships
Includes `sys/note.h`. Used by USB HID client drivers and consumers that issue HID ioctls or parse HID descriptors.

## Research Notes
This header is a mix of USB HID wire constants and illumos HID driver control codes; the report type values include request direction/type encoding.
