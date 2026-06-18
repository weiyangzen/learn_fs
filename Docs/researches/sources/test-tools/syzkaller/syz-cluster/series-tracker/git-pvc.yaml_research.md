## sources/test-tools/syzkaller/syz-cluster/series-tracker/git-pvc.yaml

This manifest defines `series-tracker-repo-disk-claim`, a `ReadWriteOnce` PVC requesting 25Gi on storage class `standard`. It persists git clones of lore archive epochs used by `series-tracker`.

Integration is direct through the series-tracker deployment. Risks include fixed capacity, storage-class environment dependence, and one-writer access limiting horizontal scaling.
