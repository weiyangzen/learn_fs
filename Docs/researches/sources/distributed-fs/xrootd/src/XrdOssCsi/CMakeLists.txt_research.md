# sources/distributed-fs/xrootd/src/XrdOssCsi/CMakeLists.txt

Purpose: builds the XrdOssCsi OSS plugin module named `XrdOssCsi-${PLUGIN_VERSION}` and installs it under the library directory.

Important build surface: the module includes checksum-sidecar core files (`XrdOssCsi.cc/.hh`, config, CRC utilities, file/AIO, pages, unaligned pages, ranges, tagstore file, trace, and handler headers). It links privately against `XrdUtils` and `XrdServer`. The installed artifact is a `MODULE` library, matching XRootD plugin loading conventions rather than a normal shared library linked by applications.

Integration/dependencies: source list shows that the requested files are only part of the plugin; important behavior also lives in `XrdOssCsiPagesUnaligned.cc`, `XrdOssCsiRanges.cc/.hh`, and `XrdOssCsiTagstoreFile.cc/.hh`. The exported plugin entry point is implemented in `XrdOssCsi.cc` as `XrdOssAddStorageSystem2`.

Risks/test signals: build risks are missing source list updates when adding new CSI components, ABI coupling to `${PLUGIN_VERSION}`, and hidden dependency on lib/server symbols supplied by XRootD. Test signals are CMake configure/build of the module, plugin loading in an XRootD server, and installation path verification.
