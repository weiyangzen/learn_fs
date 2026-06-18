# sources/test-tools/xfstests-bld/test-appliance/syz/group

Purpose: xfstests group file registering syzkaller reproducer test `001`.

Important behavior: contains `001 syz`, placing test 001 in the `syz` group.

State and dependencies: no runtime state; consumed by xfstests group selection.

Integration points: lets `./check -g syz` or equivalent run the syzkaller wrapper.

Risks and test signals: group membership is minimal. Validation is that xfstests discovers `syz/001` when selecting group `syz`.
