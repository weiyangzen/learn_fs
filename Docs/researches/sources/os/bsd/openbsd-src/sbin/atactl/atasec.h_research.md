# File Research: sources/os/bsd/openbsd-src/sbin/atactl/atasec.h

ATA Security Mode definitions for `atactl`.

It defines the security command opcodes for setting passwords, unlocking, erase prepare/unit, freeze lock, and disabling passwords. It also defines the 512-byte password sector layout with control flags for user/master passwords, normal/enhanced erase, high/maximum security level, a 32-byte password field, master password revision, and reserved padding.
