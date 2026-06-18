# File Research: sources/local-fs/udftools/pktsetup/pktsetup.rules

## Role

udev automation rules for creating/removing pktcdvd mappings for compatible optical media.

## Behavior

- Applies only to block devices with `ID_CDROM=1`.
- Removes pktcdvd mapping on device removal, missing media, or eject request.
- Allows only media types supported by kernel `pktcdvd.ko`: CD-RW, DVD+RW, DVD-RW, and DVD-RAM.
- Runs `/usr/sbin/pktcdvd-check -q $devnode`; success jumps to add, failure removes mapping.
- Adds mapping with `/usr/sbin/pktsetup -i $major:$minor`.
- Removes mapping with `/usr/sbin/pktsetup -i -d $major:$minor`.

## Research Notes

This rule depends on fixed installed paths under `/usr/sbin` and on `pktcdvd-check` exit status as the compatibility gate.
