# File Research: sources/virtualization/libguestfs/daemon/base64.c

Implements base64 FileIn/FileOut transfer helpers using the external `base64` utility.

Key points:
- `do_base64_in` receives uploaded base64 data and pipes it into `base64 -d -i > /sysroot/path`.
- Uses `sysroot_shell_quote` for destination quoting and `receive_file` for streaming input.
- Cancels input transfer correctly on command setup or write failure.
- `do_base64_out` verifies the target exists and is not a directory, then streams `base64 file` output to the client.
- Once FileOut reply is sent, later errors can only cancel the transfer via `send_file_end(1)`.
