# File Research: sources/teaching/os161/kern/include/version.h

Small version-identification header. `BASE_VERSION` is fixed at `"2.0.3"` to identify the OS/161 base code. `GROUP_VERSION` is set to `"0"` and is intended for local course or project modifications.

There is no executable logic and no dependencies beyond include guards. It is useful for boot banners, support diagnostics, and distinguishing modified student kernels from the distributed base.

Risk is operational rather than technical: changing `BASE_VERSION` would obscure provenance, while leaving `GROUP_VERSION` unchanged after significant changes reduces traceability.
