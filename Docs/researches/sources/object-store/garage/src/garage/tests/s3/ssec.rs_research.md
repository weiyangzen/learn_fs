# sources/object-store/garage/src/garage/tests/s3/ssec.rs

Purpose: This file tests SSE-C object encryption behavior for normal objects, copy operations, multipart uploads, and upload-part-copy across encrypted and non-encrypted sources/targets.

Important APIs and types: Constants define two base64 SSE-C keys and MD5s. Tests `test_ssec_object` and `test_multipart_upload` use AWS SDK SSE-C fields, `copy_object`, `create_multipart_upload`, `upload_part`, `upload_part_copy`, `complete_multipart_upload`, and helper `test_read_encrypted`.

Control flow: The object test writes encrypted objects for small and larger data, verifies reads fail without or with wrong key and succeed with the right key, copies encrypted to plaintext, plaintext to encrypted, encrypted to encrypted with different keys, and encrypted to encrypted with same key. The MPU test creates an encrypted multipart object, reads it back through SSE-C, then creates another encrypted MPU that mixes uploaded parts and copied ranges from encrypted sources before verifying assembled content.

State and persistence behavior: The tests persist encrypted object data, encryption metadata, copied object versions, multipart part state, and assembled objects. They validate that plaintext is only exposed when correct SSE-C headers are supplied.

Dependencies and integration points: They exercise Garage's SSE-C encryption/decryption layer, metadata propagation, copy-source SSE-C validation, MPU storage, byte-range copy, and S3 SDK header mapping.

Risks: Fixed test keys are hard-coded for reproducibility. The tests assert access failure generally but do not inspect exact error codes. Payload sizes are moderate but still memory-collected. They do not cover invalid key MD5 separately from wrong keys.

Test signals: SSE-C algorithm/key-MD5 response headers, failed reads without/wrong keys, exact body reads with correct keys, plaintext copy readability, encrypted copy protection, and correct assembled bytes for encrypted multipart copy.
