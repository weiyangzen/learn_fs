# sources/security-integrity/selinux/libselinux/src/init.c

Purpose: Initializes libselinux process-global mount discovery and page size.

Important APIs/types/functions: globals are `selinux_mnt`, `selinux_page_size`, and `has_selinux_config`. Functions include `selinuxfs_exists()`, `fini_selinuxmnt()`, `set_selinuxmnt()`, constructor `init_lib()`, destructor `fini_lib()`, and internal `verify_selinuxmnt()`/`init_selinuxmnt()`.

Control flow: constructor saves errno, records page size, tries default and old SELinux mount paths, checks `/proc/filesystems`, scans `/proc/mounts` for `selinuxfs`, and records only writable selinuxfs mounts. Non-Android builds also record whether SELinux config exists. Destructor frees `selinux_mnt`.

State and persistence: process-global mount string and configuration flag persist for library lifetime. `set_selinuxmnt()` can override the mount path.

Dependencies and integration: all SELinuxfs-backed APIs depend on these globals. Uses `statfs`, `statvfs`, `/proc/filesystems`, and `/proc/mounts`.

Risks and test signals: mount discovery must preserve errno and handle containers/read-only mounts. Tests should cover default mount, old mount, scan fallback, absent selinuxfs support, read-only mount rejection, override behavior, and destructor cleanup.
