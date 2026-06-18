# sources/user-network-fs/libfuse/include/meson.build

This Meson fragment defines which libfuse headers are installed into the public `fuse3` include subdirectory.

It declares `libfuse_headers` with `fuse.h`, `fuse_common.h`, `fuse_lowlevel.h`, `fuse_opt.h`, `cuse_lowlevel.h`, `fuse_log.h`, and `fuse_daemonize.h`. If `private_cfg.get('HAVE_SERVICEMOUNT', false)` is true, it appends `fuse_service.h`. It then calls `install_headers(libfuse_headers, subdir: 'fuse3')`.

The only control flow is configure-time Meson evaluation. Persistent output is the installed include tree, and the service header changes the public SDK surface only when service-mount support is configured. It integrates with packaging, downstream builds, pkg-config consumers, and source compatibility for `<fuse3/...>` includes.

Risks include forgetting to install a public header, exposing service APIs when unsupported, hiding them when enabled, or accidentally installing private/internal headers. Test signals include installed-header checks for service enabled/disabled builds, downstream compile tests for public headers, and packaging checks that private headers stay private.
