# File Research: sources/virtualization/nbdkit/plugins/sh/examples/assemble.sh

Example shell plugin that turns an assembly fragment into a bootable 512-byte sector. It validates that it is running under nbdkit by checking `$tmpdir` and the method argument, accepts a magic `file` parameter, and symlinks the real input path into the plugin tempdir.

During `config_complete`, it emits NASM source with `org 07c00h`, pads to byte 510, appends the boot signature, and assembles a binary. It reports size 512, serves reads from the assembled binary with byte-oriented `dd`, declares writes possible but makes `pwrite` fail, and exposes `magic_config_key=file`.
