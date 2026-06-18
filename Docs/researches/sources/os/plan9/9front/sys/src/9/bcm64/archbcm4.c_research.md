# File Research: sources/os/plan9/9front/sys/src/9/bcm64/archbcm4.c

BCM2711/Raspberry Pi 4 architecture support for the ARM64 kernel.

Key responsibilities:
- Implements reset/reboot watchdog control for the Pi 4 platform.
- Feeds/disables watchdog.
- Decodes CPU type/name and prints CPU identification.
- Determines CPU count.
- Clears/writes CPU wake mailboxes and sends events.
- Registers the BCM4 architecture link hook.

Important behavior:
- Similar structure to `archbcm3.c` but with BCM2711-specific register/layout assumptions.

Dependencies:
- Power/watchdog registers, ARM64 ID registers, wake mailbox layout, and platform link selection.
