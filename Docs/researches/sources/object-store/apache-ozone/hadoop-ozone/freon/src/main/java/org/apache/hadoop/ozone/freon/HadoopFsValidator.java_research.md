## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/HadoopFsValidator.java

Purpose: Freon subcommand `dfsv`/`dfs-file-validator` that validates generated files have the same digest as the first file.

Important APIs/types/functions: `call` reads object zero's digest, starts a `file-read` timer, and runs `validateFile`. `validateFile` reads an entire file into a byte array and compares MD5 digest to the reference with `MessageDigest.isEqual`.

Control flow: initialize Hadoop FS, open `<root>/<object0>`, compute digest via `BaseFreonGenerator.getDigest(InputStream)`, then each task opens the generated path for its counter, reads bytes through `IOUtils.toByteArray`, computes digest, and throws on mismatch.

State and persistence behavior: read-only against Hadoop FS. Stores reference digest locally.

Dependencies and integration points: pairs with `HadoopFsGenerator`, extends `HadoopBaseFreonGenerator`, uses commons-io and Java digest comparison.

Risks: reads whole files into memory, so large validation objects can exhaust heap; assumes all generated files have identical content, which is true for a single `ContentGenerator` run but not necessarily across independent generator invocations.

Test signals: digest mismatch throws; missing file or read error is counted as Freon task failure.
