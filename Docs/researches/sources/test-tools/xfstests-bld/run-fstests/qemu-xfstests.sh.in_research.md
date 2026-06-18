# sources/test-tools/xfstests-bld/run-fstests/qemu-xfstests.sh.in

Purpose: compatibility wrapper template that points `qemu-xfstests` style invocations at the same implementation as `kvm-xfstests`.

Important control flow: substitutes `@DIR@`, exports `KVM_XFSTESTS_DIR=$DIR/run-fstests`, and execs `$KVM_XFSTESTS_DIR/kvm-xfstests "$@"`.

State/persistence: none directly.

Dependencies/integration: provides alternate installed command name while reusing kvm runner implementation.

Risks: name may imply non-KVM behavior, but it does not alter acceleration or options; users must configure `kvm-xfstests` options.

Test signals: wrapper smoke test should produce identical behavior to kvm wrapper for no-action commands.
