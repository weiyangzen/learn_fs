## sources/test-tools/kdevops/workflows/fstests/osfiles/ol/helpers.sh

Purpose: Provides Oracle Linux oscheck hooks for release display, XFS skip groups, and distro-kernel detection.

Important APIs/types/functions: Implements `ol_read_osfile`, `ol_skip_groups`, and `ol_distro_kernel_check`.

Control flow: Reads release metadata from `/etc/os-release`, always skips XFS `encrypt`, and identifies distro kernels by asking rpm which package owns `/boot/config-$(uname -r)`.

State and persistence: Only shell variables are mutated (`VERSION_ID`, `PRETTY_NAME`, `SKIP_GROUPS`, `_SKIP_GROUPS`). No files are written.

Dependencies and integration points: Loaded dynamically by oscheck when `ID=ol`. Requires rpm database availability for kernel classification.

Risks and test signals: Minimal release-specific expunge coverage can under-triage known failures. Test with `oscheck-get-failures.sh` on OL images and compare with expected distro expunge policy.
