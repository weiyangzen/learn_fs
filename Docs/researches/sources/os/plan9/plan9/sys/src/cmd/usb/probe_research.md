# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/probe

Small rc script to list USB devices from `/dev/usb/ctl`.

Behavior:
- Binds `#u` to `/dev` if `/dev/usb` does not exist.
- Optional `-h` filters out root hubs and hubs.
- Uses `awk` to pair enabled endpoint-zero lines with the following descriptive line from `/dev/usb/ctl`.
- Prints device endpoint plus information and exits successfully.

This is a diagnostic helper, not a C driver.
