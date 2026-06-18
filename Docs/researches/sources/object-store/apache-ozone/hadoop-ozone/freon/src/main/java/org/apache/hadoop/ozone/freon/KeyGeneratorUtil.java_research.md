## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/KeyGeneratorUtil.java

Purpose: utility for deterministic Freon key-name generation.

Important APIs/types/functions: constants `PURE_INDEX`, `MD5`, and `FILE_DIR_SEPARATOR`. Methods `generatePureIndexKeyName`, `pureIndexKeyNameFunc`, `generateMd5KeyName`, and `md5KeyNameFunc`.

Control flow: pure-index methods stringify numeric indexes. MD5 methods hash the decimal number string and return the first seven hex characters.

State and persistence behavior: stateless. Names influence persistent Ozone keys created by callers.

Dependencies and integration points: used by `OzoneClientKeyReadWriteListOps` and related key-range generators to choose contiguous or distributed key names.

Risks: seven-character MD5 prefix can collide for large ranges; pure index ordering differs from zero-padded ordering used by `OmMetadataGenerator`.

Test signals: deterministic name output for representative indexes and collision considerations for benchmark ranges.
