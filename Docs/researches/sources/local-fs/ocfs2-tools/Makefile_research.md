# File Research: sources/local-fs/ocfs2-tools/Makefile

## Role

The top-level `Makefile` orchestrates the full `ocfs2-tools` build, distribution packaging, pkg-config installation, and cleanup.

## Build Graph

It includes `Preamble.make`, defines build ordering across subdirectory tiers, and ensures `include` builds before internal libraries, `libocfs2` builds after those libraries, and command/tool directories build after `libocfs2`.

The main tool tier includes fsck, mkfs, mounted, tunefs, debugfs, cluster control, heartbeat control, mount, controld, image/info/monitor tools, extras, fswreck, and defragfs. `ocfs2console` is conditionally added, and `vendor` is always added last.

## Distribution And Install

It defines pkg-config templates, Debian packaging files, project distribution files, `dist` archive creation, `distclean`, and installation of generated `.pc` files into `$(libdir)/pkgconfig`.

## Platform Notes

The file detects SUSE packaging conventions to select Python GTK package names, chkconfig dependencies, and Python bytecode compilation behavior. RPM build tooling is discovered dynamically.
