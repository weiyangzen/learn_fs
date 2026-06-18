# File Research: sources/local-fs/udftools/pktsetup/pktcdvd-check.c

## Role

Standalone validator used to determine whether an optical device/media combination can be used with the Linux `pktcdvd` packet-writing driver.

## Main Flow

- Ensures stdin/stdout/stderr are open, replacing closed descriptors with `/dev/null`.
- Parses optional `-q`/`--quiet` plus required device path.
- Opens the target read-only and verifies it is a block device.
- Uses `CDROM_GET_CAPABILITY` to ensure it is an optical device and not an existing pktcdvd device.
- Requires `CDC_GENERIC_PACKET`.
- Sends MMC `INQUIRY` and requires peripheral device type `0x05`.
- Attempts `GET_CONFIGURATION` to get the current MMC profile; falls back to disc/track info for older drives.
- Reads disc information and track/rzone information in two-stage length-aware commands.
- Validates supported media and formatting constraints.

## Compatibility Rules

Accepted profiles are CD-RW, DVD-RAM, DVD-RW restricted overwrite, DVD+RW, or unknown/pre-MMC2 with CD-RW-style checks. It rejects unsupported profile types, non-erasable CD-RW cases, reserved sessions, non-packet/non-overwritable track modes, blank/unformatted CD-RW/DVD-RW, invalid packet sizes, and non Mode 1/2 tracks.

## Dependencies

- Linux `CDROM_SEND_PACKET` and MMC command definitions from `linux/cdrom.h`.
- Endian helpers from `bswap.h`.

## Research Notes

This program’s exit status is designed for udev `PROGRAM=...` use: success means the rule should create/keep pktcdvd mapping; failure means remove or skip mapping.
