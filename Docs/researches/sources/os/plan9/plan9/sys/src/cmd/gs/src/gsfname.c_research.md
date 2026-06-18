# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfname.c

## Role

Utility implementation for parsing Ghostscript file names into optional `%device%` and file-name components.

## Main Data

Operates on `gs_parsed_file_name_t`, storing allocator ownership, `gx_io_device`, pointer to file name bytes, and length.

## Control Flow

`gs_parse_file_name` identifies `%device`, `%device%`, or `%device%name` forms and resolves devices with `gs_findiodevice`; plain names use no explicit device. `gs_parse_real_file_name` rejects device-only names and terminates the file name. `gs_terminate_file_name` sets default IO device when needed and allocates a null-terminated copy. `gs_free_file_name` frees copied names.

## Dependencies

Uses Ghostscript memory, error, type, and IO-device interfaces: `gsmemory.h`, `gxiodev.h`, `gserrors.h`.

## Notes

Empty names and unknown devices return `undefinedfilename`; device-only real names return `invalidfileaccess`.
