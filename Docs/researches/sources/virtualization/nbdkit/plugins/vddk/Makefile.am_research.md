# File Research: sources/virtualization/nbdkit/plugins/vddk/Makefile.am

Builds the VMware VDDK plugin when VDDK support is configured, excluding Windows.

Key behavior:
- Distributes `nbdkit-vddk-plugin.pod` and `README.VDDK`.
- Guards build with `HAVE_VDDK` and `!IS_WINDOWS`.
- Builds `nbdkit-vddk-plugin.la` from `vddk.c`, `vddk.h`, `reexec.c`, `stats.c`, `utils.c`, `vddk-structs.h`, `vddk-stubs.h`, `worker.c`, and the plugin header.
- Defines `VDDK_LIBDIR` as `$(libdir)/vmware-vix-disklib`.
- Includes common utility headers and links `common/utils/libutils.la`, `DL_LIBS`, and Windows import support.
- Adds the plugin version script when enabled.
- Generates `nbdkit-vddk-plugin.1` from POD with magic-parameter insertion when POD support is present.

Dependencies:
- dlopen/dlsym library support.
- nbdkit common utils.
- VDDK installed at runtime, loaded dynamically rather than directly linked.
