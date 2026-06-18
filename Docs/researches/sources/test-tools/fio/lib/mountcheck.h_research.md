# sources/test-tools/fio/lib/mountcheck.h

Purpose: declares `device_is_mounted`.

Important APIs/functions: `int device_is_mounted(const char *)`, returning nonzero when the configured platform implementation finds the device in the mount table.

Control flow/state: no state in the header; callers query synchronously.

Dependencies/integration: implementation is platform-selected. Used by code that wants to warn or refuse operations on mounted devices.

Risks/test signals: return 0 can mean "not mounted" or "mount enumeration unsupported/unavailable." Callers should account for that ambiguity.
