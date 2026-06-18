# sources/user-network-fs/nfs-ganesha/src/config_samples/ceph.conf

## Purpose

`ceph.conf` is a sample NFS-Ganesha configuration for exporting CephFS through FSAL_CEPH, with optional RADOS-backed recovery and RADOS-backed configuration includes.

## Important APIs, Types, and Functions

The sample exercises config blocks `NFS_CORE_PARAM`, `NFSv4`, `MDCACHE`, `EXPORT`, nested `FSAL`, `CEPH`, `RADOS_KV`, and `RADOS_URLS`. It documents `%url rados://pool/namespace/object` usage.

## Control Flow

The config disables NLM and rquotad, restricts protocols to NFSv4, prefers NFSv4.1/4.2, minimizes MDCACHE directory chunking, defines a CephFS export at `/` with pseudo path `/cephfs_a/`, and selects FSAL `CEPH`. Later blocks provide optional Ceph cluster, recovery, and config-URL parameters.

## State and Persistence Behavior

At runtime this configuration can use Ceph for exported filesystem state, recovery records, and even configuration storage. Defaults leave many Ceph authentication and recovery parameters commented, so actual persistence depends on administrator-provided values.

## Dependencies and Integration Points

It integrates with FSAL_CEPH, libcephfs, RADOS recovery backends, `RADOS_URLS`, NFSv4 recovery, MDCACHE, and export handling. It is also a parser regression sample covering nested blocks, strings, booleans, integers, and comments.

## Risks and Edge Cases

The sample exports `/` because FSAL_CEPH lacks subtree checking, which is correct for safety but broad. It warns delegations are not recommended in clustered configurations. RADOS URL/recovery comments imply separate Ceph clients and keyring requirements that operators must satisfy.

## Test Signals

`verif_syntax` should accept the sample. Integration tests require a Ceph cluster and should validate NFSv4 mount, recovery backend selection, FSAL_CEPH auth, and optional `RADOS_URLS` fetch/watch behavior.
