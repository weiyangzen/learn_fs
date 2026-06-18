# sources/user-network-fs/samba/source4/lib/policy/samba-policy.pc.in

`samba-policy.pc.in` is the pkg-config template for the `samba-policy` library. It declares install prefix variables, package name and description, public `Requires: talloc`, private `Requires.private: ldb`, package version substitution, linker flags for `-lsamba-policy`, and include flags with `-DHAVE_IMMEDIATE_STRUCTURES=1`.

The file has no runtime control flow or persistence, but it defines the external build integration contract for consumers outside the Samba Waf build. The dependency split exposes talloc publicly while keeping LDB private unless static linking or private resolution is needed.

Risks are packaging-related: missing dependencies can break external builds, the immediate-structures define may leak Samba internals into consumers, and version/library path substitutions must match install layout. Test signals include `pkg-config --cflags --libs samba-policy` after install and compiling a small consumer that includes `policy.h` and links against `libsamba-policy`.
