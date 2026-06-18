# File Research: sources/os/bsd/openbsd-src/sbin/mountd/Makefile

This Makefile builds `mountd`, installs `exports.5` and `mountd.8`, links against `libutil`, and disables default static linking by clearing `LDSTATIC`.

Only the build file is in this group; the `mountd` daemon source itself is outside the listed file set.
