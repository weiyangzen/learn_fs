# sources/test-tools/syzkaller/prog/images_test.go

Purpose: verifies extraction of compressed filesystem image assets from programs.

Important APIs/types/functions: package-level `flagUpdate` and `TestForEachAsset`.

Control flow and state: the test loads Linux/amd64, scans `testdata/fs_images/*.in`, deserializes each program, calls `Prog.ForEachAsset`, reads each asset stream, optionally updates golden output files, compares bytes to `*.out_mount_N`, and verifies every existing output file was used.

Dependencies and integration: uses `GetTarget`, `Deserialize`, `ForEachAsset`, `AssetType`, `MountInRepro`, `osutil.WriteFile`, filesystem testdata, and `testify/require`.

Risks: `-update` mutates golden files intentionally. The test is sensitive to testdata layout and asset naming (`mount_<call index>`). It assumes compressed image deserialization succeeds before asset extraction.

Test signals: direct coverage for compressed image decompression, asset callback metadata, syscall association, output naming, and completeness of golden assets.
