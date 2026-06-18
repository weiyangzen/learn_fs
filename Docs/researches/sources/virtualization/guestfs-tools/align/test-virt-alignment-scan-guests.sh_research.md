# File Research: sources/virtualization/guestfs-tools/align/test-virt-alignment-scan-guests.sh

## Scope

Libvirt-backed integration smoke test for `virt-alignment-scan`.

## Behavior

- Uses the phony guest libvirt XML through `test://$abs_top_builddir/test-data/phony-guests/guests-all-good.xml`.
- Runs `virt-alignment-scan -c "$libvirt_uri"`.
- Accepts exit codes `0`, `2`, and `3` because those are semantic alignment results, not execution failures.

## Dependencies And Risks

- Depends on libvirt test driver support and generated phony guest metadata.
- Does not assert exact output, only that the tool completes with a valid alignment-result code.
