## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OzoneClientKeyValidator.java

Purpose: Freon subcommand `ockv`/`ozone-client-key-validator` that verifies generated Ozone keys have the same digest as key zero.

Important APIs/types/functions: options configure volume, bucket, stream digest mode, and OM service ID. Methods include `call`, `readReference`, `getKeySize`, `validateKey`, `getDigest(String)`, `calculateDigestStreaming`, `readKeyToByteArray`, `readKey`, and `validateDigest`.

Control flow: initialize Freon, create Ozone client, read reference digest from object zero. If non-stream mode and key size exceeds byte-array capacity, switch to streaming. Then run validation tasks: read each key by generated name, calculate digest either during stream read or after loading to byte array, compare with reference, and close client.

State and persistence behavior: read-only against Ozone keys. Local state stores reference digest, reference key size, timer, stream mode, and client.

Dependencies and integration points: pairs with `OzoneClientKeyGenerator`, uses `BaseFreonGenerator.getDigest`, commons IO, and Ratis checked function.

Risks: non-stream mode reads whole keys into memory; generated keys must share identical content and size; client close is not in finally if validation throws.

Test signals: digest mismatch throws; large key path should force streaming; successful validation confirms readable generated data.
