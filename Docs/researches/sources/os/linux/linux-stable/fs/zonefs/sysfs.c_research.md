# File Research: sources/os/linux/linux-stable/fs/zonefs/sysfs.c

## Purpose

Implements zonefs sysfs attributes under the global `fs/zonefs` kobject.

## Main Responsibilities

- Defines read-only sysfs attributes for max/current write-open sequential files.
- Defines read-only sysfs attributes for max/current active sequential files.
- Registers a per-superblock kobject named after the superblock id.
- Unregisters and waits for kobject release during teardown.
- Initializes and exits the global zonefs sysfs root.

## Important Invariants

- Per-superblock sysfs unregister waits for release completion.
- Attribute show dispatch uses container lookup from kobject and attribute.
- Registration state prevents double unregister.

## Dependencies

Uses sysfs/kobject APIs, superblock sysfs naming, and zonefs superblock info fields.

## Research Notes

Small observability layer for device open/active zone resource tracking.
