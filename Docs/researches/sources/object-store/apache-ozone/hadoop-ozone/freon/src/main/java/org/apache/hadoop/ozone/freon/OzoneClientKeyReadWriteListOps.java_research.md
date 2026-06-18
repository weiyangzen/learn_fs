## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OzoneClientKeyReadWriteListOps.java

Purpose: Freon subcommand `ockrw` that mixes read, write, and list operations over a bounded key range from multiple Ozone clients.

Important APIs/types/functions: options configure volume, bucket, metadata-only reads, start index, range, object size, contiguous vs MD5 key naming, linear vs random selection, read/list percentages, max list result, and OM service ID. Methods include `call`, `readWriteListKeys`, `processReadTasks`, `processWriteTasks`, `processListTasks`, `decideReadWriteOrListTask`, and `getKeyName`. Enum `TaskType` has read/write/list.

Control flow: initialize Freon, create one Ozone client per Freon thread, ensure target bucket, prepare random key content, initialize `KeyGeneratorUtil`, and run tasks. Each task selects a client by counter, chooses task type by random percentage, chooses key name either linearly or randomly in range, and performs read, write, or list through client proxy.

State and persistence behavior: writes keys and reads/lists existing keys in the target bucket. Static `NEXT_NUMBER` coordinates linear key selection across instances in the JVM.

Dependencies and integration points: Ozone client proxy, `KeyGeneratorUtil`, commons IO/random, metrics.

Risks: percentage values are not bounded to 0-100; static linear counter persists across runs; MD5 seven-character names can collide; metadata-only read still requires key existence.

Test signals: distribution of task types, key naming mode, successful read/write/list against prepared ranges, and client cleanup.
