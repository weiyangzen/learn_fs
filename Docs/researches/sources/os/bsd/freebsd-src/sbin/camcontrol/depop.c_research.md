# File Research: sources/os/bsd/freebsd-src/sbin/camcontrol/depop.c

## Purpose
Implements SCSI disk head depopulation commands: list physical elements, remove/truncate an element, and restore/rebuild elements.

## Main Elements
- `depop_list()`: sends GET PHYSICAL ELEMENT STATUS and prints element ID, restore eligibility, health, type, and capacity.
- `depop_remove()`: sends REMOVE ELEMENT AND TRUNCATE for an element and/or capacity.
- `depop_restore()`: sends RESTORE ELEMENTS AND REBUILD.
- `depop()`: parses `-c`, `-e`, `-d`, `-l`, `-r`; enforces a single action; chooses timeouts.

## Dependencies And Integration
Uses CAM, SCSI wrapper helpers, physical element status structures, and SCSI depopulation commands.

## Behavioral Notes
Default timeout is 5 seconds for listing. For remove/restore it uses block device characteristics VPD `depopulation_time` when present, otherwise one day.

## Risk Notes
Remove/restore operations are disruptive storage maintenance commands. The file comments note depop can make drives format-corrupt until the operation completes or is repeated.
