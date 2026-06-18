# File Research: sources/os/bsd/openbsd-src/sbin/iked/version.h

This tiny header defines the OpenIKED version string.

Key content:
- `#define IKED_VERSION "7.4"`

Usage:
- Consumed wherever OpenIKED needs to report or embed its version, including vendor/version-identification paths.

Security and correctness notes:
- No logic, state, or OS interaction.
