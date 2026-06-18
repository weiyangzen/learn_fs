## sources/test-tools/syzkaller/tools/android/jni/Application.mk

This NDK application makefile selects `APP_ABI := arm64-v8a` and `APP_PLATFORM := latest`. It also includes `CLEAR_VARS`, though that is more typical in `Android.mk`.

Integration is with `ndk-build` for the Android sandbox test. Risks include only building arm64 and using `latest`, which may differ across installed NDK versions.
