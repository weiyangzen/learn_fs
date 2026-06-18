## sources/test-tools/kdevops/workflows/fstests/ext4/Kconfig

Purpose: Defines ext4 fstests section coverage, including default ext4 profiles, small block sizes, bigalloc cluster sizes, and advanced feature testing.

Important APIs/types/functions: Main symbols are `HAVE_DISTRO_EXT4_PREFERS_MANUAL`, `FSTESTS_EXT4_MANUAL_COVERAGE`, and `FSTESTS_EXT4_SECTION_*` selectors for defaults, 1K/2K/4K blocks, bigalloc cluster sizes, and advanced features.

Control flow: Manual mode exposes all section choices. Non-manual mode enables only the default and advanced feature sections by default, avoiding the larger manual block-size/bigalloc matrix.

State and persistence: Kconfig selections persist to `.config` and are used by the fstests host-generation logic. The file writes no runtime state.

Dependencies and integration points: Sourced by the parent fstests Kconfig when `FSTESTS_EXT4` is active. Section names must align with fstests config templates and oscheck section parsing.

Risks and test signals: Several help strings mention "1k block size" for multiple sections, which could confuse users even though symbol names differ. Test by verifying generated ext4 sections and mkfs options in host configs.
