# sources/test-tools/syzkaller/pkg/csource/testdata/1

This fixture captures an iommufd-oriented syscall sequence and expected csource formatting. The input opens `/dev/iommu`, allocates an IOAS, maps pages, creates access, and performs a syzkaller-specific access-pages ioctl.

The important APIs represented are `openat$iommufd` and several `ioctl$IOMMU_*` variants. The expected output verifies native syscall collapse to `__NR_openat` and `__NR_ioctl`, resource propagation through `r[0]`, `r[1]`, and `r[2]`, struct field comments, output-resource annotations, VMA pointer rendering, and flag/constant naming.

State is textual fixture data; persistence is the checked-in expected output. Dependencies are Linux/amd64 syscall descriptions and csource comment formatting. Integration is through the syscall-generation snapshot test. Risks include kernel description drift, changed IOMMU constants, and formatter output changes. The test signal is useful for complex nested structs, in/out resources, ioctl command constants, and syzkaller pseudo-variant formatting.
