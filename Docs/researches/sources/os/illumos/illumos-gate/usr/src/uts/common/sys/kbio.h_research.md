# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kbio.h

## Role

`kbio.h` defines keyboard-related ioctl numbers, keymap ioctl payload structures, LED/compat/layout/autorepeat/beeper controls, and x86-specific ioctl-number offsets needed to avoid historical `kd` conflicts.

## Major Definitions

The ioctl namespace is `KIOC` as `('k' << 8)`. `KIOCTRANS`, `KIOCGTRANS`, `KIOCTRANSABLE`, and `KIOCGTRANSABLE` set/query translation mode and whether table translation is possible, with x86-compatible values offset by 30 for conflict avoidance. `TR_CANNOT` and `TR_CAN` report table translatability.

`struct kiockey` is the old-style keymap entry with an 8-bit entry value and special tablemask values for abort key stations. `struct kiockeymap` is the new-style entry with an unsigned keymap entry. `KIOCSETKEY`/`KIOCGETKEY` and `KIOCSKEY`/`KIOCGKEY` set/query keymap entries and string table values. Other ioctls control keyboard commands, type, direct-to-console routing, LEDs, compatibility mode, layout, abort behavior, autorepeat delay/rate/count, beeper frequency, and tone generation.

Abort controls define disable, hardware BREAK enable, and alternate-abort modes. `struct freq_request` selects console or keyboard beeper and a frequency; `KIOCMKTONE` uses historical i8254 clock cycles with `PIT_HZ` defined as 1193182 and aliased as `KDMKTONE`.

## Interfaces

There are no functions. The header exports ioctl request values and payload layouts for keyboard consumers and drivers.

## Integration Notes

The x86 conditional ioctl numbering is an ABI compatibility constraint. Keymap ioctl handlers must validate table masks, key stations, string lengths, and special abort-table selectors. Some ioctls are privileged or affect serial input devices as well as keyboards, especially keyboard abort configuration.
