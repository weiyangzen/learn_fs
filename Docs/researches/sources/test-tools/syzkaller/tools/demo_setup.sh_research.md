<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/demo_setup.sh -->
# sources/test-tools/syzkaller/tools/demo_setup.sh

## Purpose

Legacy demo setup that downloads pinned syzkaller/kernel/toolchain artifacts and starts qemu fuzzing.

## Important APIs, Types, and Functions

apt, curl/wget, old Go/gcc/image/corpus downloads, `go get`, git checkout, kernel clone/build, generated manager config.

## Control Flow

Installs deps, sets GOPATH/PATH, downloads artifacts, builds old syzkaller and Linux v4.13, writes manager config, starts syz-manager.

## State and Persistence Behavior

Creates go/gcc/gopath/linux/workdir/images/corpus/config under current dir.

## Dependencies and Integration Points

Depends on obsolete external artifacts, KVM/QEMU, apt hosts, old Go behavior.

## Risks and Edge Cases

Pinned old versions and downloaded binaries are unsuitable for production; artifacts may vanish.

## Test Signals

Smoke only if legacy URLs work; otherwise compare generated config to modern setup expectations.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/demo_setup.sh -->
