## sources/security-integrity/attr/configure.ac

Purpose: Autoconf configuration for libattr/tools.

It declares package `attr` 2.5.2, config headers, compiler/libtool/gettext setup, debug flags, calculated libtool revision, Linux conditional, GCC symbol-version attribute detection, and generated files. It also creates an `include/attr` symlink for in-tree include compatibility. State is configure-time substitutions and conditionals. Dependencies include Autoconf 2.69, Automake 1.15, Libtool, gettext, C compiler feature probes, and Linux host checks. Risks include fragile version parsing for `LT_REVISION`, symlink creation behavior on unusual filesystems, and Linux-only syscall wrappers behind `OS_LINUX`. Tests are `autoreconf`, `./configure` on target hosts, and symbol-version build checks.
