# sources/test-tools/syzkaller/dashboard/config/linux/bits/bluetooth.yml

Purpose: enables Bluetooth stack and common controller/protocol drivers for Bluetooth fuzzing.

Important keys: `BT`, BR/EDR, RFCOMM/TTY, BNEP filters, HIDP, LE, HS conditionals, 6LoWPAN, LEDs, Microsoft extensions, USB/uart/virtual HCI drivers, and newer LE/poll-sync options with version guards.

Control flow: declarative feature-enabling fragment.

State and persistence: affects generated `.config`.

Dependencies and integration points: Linux Bluetooth Kconfig, USB/UART HCI driver availability, syzkaller Bluetooth descriptions and manager profiles.

Risks: version guards (`BT_CMTP`, `BT_HS`, `BT_LE_L2CAP_ECRED`, `BT_HCIBTUSB_POLL_SYNC`) need maintenance. Enabling broad Bluetooth support increases attack surface and boot/device initialization paths.

Test signals: configs should build with Bluetooth enabled and syzkaller should see relevant Bluetooth devices/syscalls.
