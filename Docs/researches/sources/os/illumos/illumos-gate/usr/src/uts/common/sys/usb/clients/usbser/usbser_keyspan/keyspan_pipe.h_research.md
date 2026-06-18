# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_keyspan/keyspan_pipe.h

Keyspan USB pipe management header. It defines `keyspan_pipe_t`, which wraps a mutex, parent state pointer, pipe handle, endpoint descriptor, pipe policy, state, and log handle.

Pipe states are not-initialized, closed, and open. Function prototypes cover device-specific pipe initialization/finalization, open/close/reopen flows for device and port pipes, shared close helpers, data receive/send paths, status receive, and polling startup.

It depends on forward-declared `keyspan_state_t` and `keyspan_port_t` from `keyspan_var.h`.
