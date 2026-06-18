# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hubd/hub.h

USB hub protocol definition header. It defines USB 2 hub descriptors, packed USB 3 SuperSpeed hub descriptors, root-hub descriptor constants, hub-characteristic bits, class request types, hub and port status/change bits, feature selectors, USB 3 status extensions, and remote wake mask values.

The file normalizes the hub-class vocabulary used by physical hub drivers and HCD root-hub emulation. It includes compatibility notes for USB 2 versus USB 3 differences, especially port power/status bit location and extended USB 3 link/config changes.

Important limits include `MAX_PORTS` set to 31 for current hubd simplicity, while USB specifications allow more. xHCI private ioctls separately allow 256 port status slots for controller diagnostics.
