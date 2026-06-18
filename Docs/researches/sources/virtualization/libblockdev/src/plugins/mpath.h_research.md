# File Research: sources/virtualization/libblockdev/src/plugins/mpath.h

## Role
Public header for the multipath plugin.

## API Surface
Declares the error domain, error codes, technology/mode enums, lifecycle, availability, map flushing, member detection, member listing, and friendly-name configuration.

## Design Notes
The API is deliberately small: it does not create maps directly, but detects and flushes them and controls a common `mpathconf` setting.
