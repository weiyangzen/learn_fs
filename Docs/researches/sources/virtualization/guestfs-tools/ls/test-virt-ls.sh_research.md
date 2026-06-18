# File Research: sources/virtualization/guestfs-tools/ls/test-virt-ls.sh

## Role

Functional regression test for `virt-ls`.

## Behavior

The script first checks exact plain listing output for `/bin` in the Fedora phony image. Expected names are `ls`, `rpm`, `sh`, and `test1` through `test7`.

It then checks `virt-ls -lR` on `/boot`, piping through `awk` to compare selected columns: file type/permissions, size field, and path. The expected tree includes `/boot`, `/boot/grub`, `grub.conf`, an initramfs, `lost+found`, and a vmlinuz file.

Finally it invokes old-style `virt-ls -l` and `virt-ls -R` syntaxes against the Fedora image as smoke checks.

## Research Notes

The test validates both modern option syntax and legacy positional image syntax.
