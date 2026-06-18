# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/416

Purpose: Linux reporter parse fixture for syzkaller. It expects `KASAN: use-after-free Write in video_unregister_device`, alternate `bad-access in video_unregister_device`, type `KASAN-USE-AFTER-FREE-WRITE`, corrupted `N`, panicked `N`. The log covers video device unregister after USBVision lifetime corruption.

Important APIs, types, and functions: this static fixture exercises KASAN write UAF parsing. Important frames include `kobject_del`, `device_del`, `device_unregister`, `video_unregister_device`, `usbvision_unregister_video`, and `usbvision_release`.

Control flow: 108 log lines are parsed. KASAN reports a write in kobject/device deletion, and the title extractor must select the media subsystem unregister site.

State and persistence behavior: expected state is in headers; runtime parsing is temporary and read-only.

Dependencies, integration points, risks, and test signals: this integrates KASAN parsing with V4L/media driver teardown deduplication. Risks are grouping under `kobject_del` or `device_del` instead of `video_unregister_device`. Passing tests require UAF-write classification, bad-access alternate, and no panic/corruption.
