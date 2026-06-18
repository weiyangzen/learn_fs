# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/ServerUtils.java

## Purpose

`ServerUtils` provides shared HDDS/Ozone server helpers for configuration sanitization, RPC listen address updates, metadata/DB directory resolution and permissions, remote user lookup, and default Ratis directory selection with upgrade compatibility.

## Important APIs, Types, and Functions

`sanitizeUserArgs` clamps a value to min/max factors of a base value. `updateRPCListenAddress` and `updateListenAddress` update `OzoneConfiguration` after binding. `getScmDbDir`, `getDBPath`, and `getOzoneMetaDirPath` resolve metadata directories. `getDirectoryFromConfig` enforces single directory, creates it, and sets POSIX permissions. `getPermissions`, `getSymbolicPermission`, and `setDataDirectoryPermissions` handle configured modes. `getRemoteUserName` wraps Hadoop IPC server state. `getDefaultRatisDirectory` and `getDefaultRatisSnapshotDirectory` derive component-specific paths, checking legacy SCM/shared Ratis locations through `findExistingRatisDirectory`.

## Control Flow

Most methods validate config, create directories when missing, set permissions, and return concrete paths. Ratis directory fallback first checks old non-empty directories to preserve upgrade behavior, otherwise returns a new component-specific path under `ozone.metadata.dirs`.

## State and Persistence Behavior

No class state. It creates directories and changes POSIX permissions on disk, and mutates `OzoneConfiguration` for listen addresses and metadata path setters.

## Dependencies and Integration Points

It depends on HDDS/Ozone/SCM/Recon config keys, Hadoop IPC `Server`, Hadoop filesystem permissions, Java NIO file APIs, protobuf `NodeType`, and logging.

## Risks and Edge Cases

`getDirectoryFromConfig` rejects multiple metadata dirs for components that do not support them. POSIX permission APIs can fail on non-POSIX filesystems. `setDataDirectoryPermissions` logs warnings instead of failing startup. `getComponentName` throws for new enum values until updated.

## Test Signals

Test clamp boundaries, listen-address mutation, missing/multiple directory config, octal and symbolic permission conversion, non-writable permission skip, fallback to metadata dirs, legacy Ratis path detection, snapshot path naming, and remote user null handling.
