# sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/uapi/unused_ioctl.h

Purpose: this UAPI fixture defines an ioctl constant that is intentionally used only by an otherwise unused file operation table.

Important APIs and flow: includes `ioctl.h` and defines `UNUSED_IOCTL1` as `_IO('c', 1)`.

State and persistence: macro only.

Dependencies and integration: included by `file_operations.c`, where `UNUSED_IOCTL1` and a local `UNUSED_IOCTL2` appear in `unused_ioctl`. The extraction pipeline should avoid turning unreachable unused operations into final descriptions.

Risks: if reachability pruning changes, this constant may appear or disappear in generated output.

Test signals: validates unused-interface pruning and include/constant usage accounting.
