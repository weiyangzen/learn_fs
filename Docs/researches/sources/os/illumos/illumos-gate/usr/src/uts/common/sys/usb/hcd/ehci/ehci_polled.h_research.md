# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci_polled.h

EHCI polled-mode state header for firmware/debugger console operation. It defines raw buffer size, input/output mode flags, in-use flags, keyboard packet limit, and `ehci_polled_t`.

`ehci_polled_t` stores controller state pointer, input pipe handle, dummy and interrupt QHs, raw scan-code buffer, flags, active interrupt QTD list, nested enter/exit reference count, saved USB device pointer, endpoint address, and a no-sync workaround flag.

The comments document nested polled entry/exit behavior through kmdb and firmware prompts so controller state is restored only after the final exit.
