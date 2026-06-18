# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFSWithObjectStoreCreate.java

Purpose: abstract non-HA integration tests for interactions between object-store-created keys and O3FS filesystem path semantics in legacy buckets with filesystem paths enabled.

Important APIs/types/functions: setup enables `OmConfig.fileSystemPathEnabled`, creates a fresh legacy volume/bucket for each test, and opens `OzoneFileSystem`. Tests include object-store key creation with slashy paths, O3FS status of ancestors, object-store delete plus O3FS recursive delete/rename, key close failure when a directory appears before commit, MPU complete failure/success around same-name directory conflicts, directory-first conflicts, non-normalized `listKeys`, and double-slash prefix normalization. Helpers `checkKeyList`, `createAndAssertKey`, `readKey`, `checkPath`, and `checkAncestors` centralize verification.

Control flow: each scenario creates keys through `OzoneBucket` APIs, then reads or mutates through O3FS. Conflict tests deliberately create an object-store stream or multipart part, create a filesystem directory at the same path before commit/complete, assert `NOT_A_FILE`, remove the directory if needed, and retry.

State and persistence behavior: validates normalization from leading or repeated slashes to canonical key names, implicit ancestor directories, deletion of synthetic parents after object-store key removal, and correct persistence of MPU parts only after complete succeeds. Same path cannot be both directory and file/key.

Dependencies and integration points: uses `OzoneClient`, `OzoneBucket`, `OzoneVolume`, `OzoneOutputStream`, MPU metadata/ETag calculation, `OmUtils.normalizeKey`, `OzoneFileSystem`, OM config, and legacy bucket layout.

Risks: path strings intentionally include leading and repeated slashes; changing normalization rules can shift many assertions. The test temporarily mutates OM config and must restore it. The MPU path depends on MD5/ETag metadata setup.

Test signals: strong signal for S3/object-store and filesystem interoperability, directory/file conflict handling, path normalization, key listing prefix/previous-key behavior, and ancestor status synthesis.
