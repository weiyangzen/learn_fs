# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_dsdi.h

USB serial Device-Specific Driver Interface. This is the core contract between the generic serial driver and concrete USB serial chip drivers.

It defines opaque DSD handles, callback registration (`ds_cb_t` for TX/RX/status), attach information, the `ds_ops_t` operation vector, operation-vector versioning, port parameter types and arrays, direction flags, on/off values, and input error codes.

`ds_ops_t` covers attach/detach, callback registration, port open/close, USB power, suspend/resume, disconnect/reconnect, UART parameter setting, modem control get/set, break, loopback, transmit, receive, stop/start, FIFO flush/drain, and V1 polled I/O pipe accessors.

The data ownership rule for `ds_tx()` is explicit: a DSD that accepts the mblk and returns success owns it afterward.
