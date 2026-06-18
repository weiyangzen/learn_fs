# sources/object-store/openstack-swift/swift/common/utils/checksum.py

## Purpose

`checksum.py` provides hashlib-like CRC hashers for Swift checksum use cases, especially S3 checksum headers. It chooses the fastest available implementation for CRC32C and CRC64-NVME across optional `anycrc`, ISA-L, and Linux kernel AF_ALG support, while always providing CRC32 through `zlib.crc32`.

## Important APIs, Types, And Functions

- `find_isal()` locates an ISA-L shared library either system-wide through `ctypes.util.find_library('isal')` or inside a `pyeclib` package installation.
- Optional implementation functions are `crc32c_isal`, `crc64nvme_isal`, `crc32c_kern`, `crc32c_anycrc`, and `crc64nvme_anycrc`.
- `_select_crc32c_impl()` chooses `crc32c_isal`, then kernel AF_ALG, then `anycrc`, raising `NotImplementedError` if none are present.
- `_select_crc64nvme_impl()` chooses ISA-L, then `anycrc`, raising `NotImplementedError` if neither is present.
- `CRCHasher` is a hashlib-style wrapper with `update()`, `digest()`, `hexdigest()`, `copy()`, `digest_size`, and `digest_fmt`.
- `crc32(data=None, initial_value=0)`, `crc32c(data=None, initial_value=0)`, and `crc64nvme(data=None, initial_value=0)` create `CRCHasher` instances.
- `log_selected_implementation(logger)` emits info/warning lines for the selected CRC32C and CRC64-NVME implementations.

## Control Flow And Behavior

Import-time detection first tries `anycrc` and creates callable model calculators when available. `find_isal()` then attempts to load ISA-L. If ISA-L exposes `crc32_iscsi`, the module configures ctypes signatures and defines `crc32c_isal()` with the required XOR pre/post processing. If ISA-L exposes `crc64_rocksoft_refl`, it configures and defines `crc64nvme_isal()`. Finally, it probes Linux AF_ALG support for `"hash", "crc32c"`; if available, `crc32c_kern()` creates a keyed AF_ALG socket per computation, sends data, and returns the kernel digest value.

`CRCHasher` stores the selected CRC function, current integer CRC, name, and width. `update()` folds new data into `self.crc`, `digest()` packs the current integer as big-endian 32-bit or 64-bit bytes, `hexdigest()` hex-encodes that packed value, and `copy()` creates a new hasher with the same function and current CRC. The public factory functions mirror hashlib constructors by accepting optional initial data.

## State And Persistence

The module keeps process-global feature-detection state: loaded ISA-L handle, optional implementation callables, and selected functions. `CRCHasher` instances hold only in-memory checksum state. There is no disk persistence.

## Dependencies And Integration Points

Dependencies include optional `anycrc`, optional `pyeclib`, `ctypes`, `ctypes.util`, `importlib.metadata`, Linux `socket.AF_ALG`, `struct`, `binascii`, and `zlib`. S3 middleware imports `swift.common.utils.checksum` for `x-amz-checksum-crc32c` and `x-amz-checksum-crc64nvme` handling. Operators can use `log_selected_implementation()` to expose runtime checksum capability.

## Risks And Edge Cases

- `hasattr(isal, ...)` is called even when `find_isal()` returns `None`; this is safe because `hasattr(None, ...)` is false, but later code depends on those globals being set to `None`.
- Kernel AF_ALG probing closes `_sock` only for the ENOENT branch; unsupported address family and successful probe paths do not retain an explicit global socket, but the temporary object is left to normal cleanup.
- CRC32C implementation selection happens on each hasher creation, so a missing optional library raises at call time rather than import time.
- `CRCHasher.digest_size` returns `self.width / 8`, a float in Python 3, unlike hashlib's integer `digest_size`.
- `update()` expects bytes-like input accepted by the selected backend; passing text will fail differently depending on backend.
- AF_ALG setup per `crc32c_kern()` call is slower but intentionally lower priority than ISA-L.
- CRC64-NVME support depends on ISA-L >= 2.31.0 or `anycrc`; older deployments will raise `NotImplementedError`.

## Test Signals

The local source snapshot has no tests directory. Expected coverage should compare known CRC32, CRC32C, and CRC64-NVME vectors across initial values and incremental `update()` calls; validate `copy()` state independence; mock ISA-L, AF_ALG, and `anycrc` availability to confirm implementation preference and `NotImplementedError` paths; assert `log_selected_implementation()` emits useful warnings; and verify S3 middleware rejects unsupported checksums predictably when optional backends are absent.
