# sources/user-network-fs/rclone/bin/test_backend_sizes.py

Purpose: estimates binary size contribution of each backend by compiling rclone with all backends, then repeatedly commenting one backend import out of `backend/all/all.go` and measuring size difference.

Important functions: `read_backends`, `write_all`, `compile`, and `main`. State changes are direct rewrites of `backend/all/all.go` and creation of `rclone` binary; the original file is restored at the end. Dependencies are Go build and backend import file format. Risks include leaving `all.go` modified if interrupted, special-case coupling for `s3`/`pikpak`, no dirty-tree guard, and measuring compile/linker interactions rather than exact isolated backend size. Test signal is produced CSV-like size output.
