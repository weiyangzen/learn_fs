# File Research: sources/virtualization/libguestfs/daemon/daemon-utils-tests-stubs.c

Test-only stubs for linking daemon utility tests without full daemon dependencies.

Key points:
- Stubs `device_name_translation`, `reply_with_error_errno`, and `reply_with_perror_errno`.
- Each stub is `noreturn` and aborts if unexpectedly called.
- Lets `daemon_utils_tests` link selected helper files without pulling protocol/device translation machinery.
