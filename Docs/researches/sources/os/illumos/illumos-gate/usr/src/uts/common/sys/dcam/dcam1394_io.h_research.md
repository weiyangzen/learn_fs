# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dcam/dcam1394_io.h

Ioctl and data-structure header for DCAM IEEE 1394 camera control. It defines camera parameter IDs, subparameters, value constants, ioctl commands, status flags, parameter-list helpers, frame records, and register read/write payloads.

Key elements:
- Parameter-list macros initialize, add/remove/test entries, and access value/error fields in a two-dimensional parameter list.
- Defines 30 parameters and 24 subparameters.
- Parameter IDs cover power, video-mode capabilities, frame-rate capabilities per video mode, current video mode/frame rate, ring-buffer capacity/ready count/read-pointer increment, frame byte size, status, and image controls such as brightness, exposure, sharpness, white balance, hue, saturation, gamma, shutter, gain, iris, focus, zoom, pan, and tilt.
- Subparameters cover video modes, frame rates, feature presence/capabilities, min/max/current values, on/off, control mode, white-balance U/V values, and none.
- Value aliases define video modes, frame rates, automatic/manual control, and power on/off.
- Ioctl commands support register read/write, camera reset, parameter get/set, frame receive start/stop, ring-buffer flush, and frame sequence counter reset.
- Status flags report frame receive completion, lost frame, parameter changes, sequence counter overflow, and camera unplug.
- `dcam1394_param_list_entry_t` stores a requested flag, error, and value; `dcam1394_param_list_t` is the fixed parameter/subparameter matrix.
- `dcam1394_frame_t` describes video mode, sequence number, timestamp, and frame buffer pointer.
- `dcam1394_reg_io_t` carries register offset/value for register access.

Dependencies:
- Includes `sys/time.h` for `hrtime_t`.
- Consumed by the DCAM 1394 driver and userland code issuing camera-control ioctls.

Research notes:
- Parameter and subparameter values intentionally alias generic indices and descriptive names, so consumers can use either naming style.
- The frame structure includes a raw buffer pointer, making ioctl handlers responsible for user/kernel pointer handling and data-size validation.
