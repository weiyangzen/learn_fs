# File Research: sources/virtualization/guestfs-tools/edit/test-virt-edit-docs.sh

Shell test for `virt-edit` documentation. It sources the shared test helpers, enables `set -e` and `set -x`, honors `skip_if_skipped`, and runs `podcheck.pl` against `virt-edit.pod`.

It validates that the POD documentation for `virt-edit` is internally consistent and checks common option documentation via `--path $top_srcdir/common/options`.

Research relevance: documentation validation fixture; no filesystem behavior beyond test harness integration.
