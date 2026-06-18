
# sources/sync-backup/restic/internal/repository/packer_uploader.go

Purpose: implements asynchronous pack upload fan-out for finalized packers.

Important types are `savePacker`, `uploadTask`, and `packerUploader`. `newPackerUploader` creates a buffered task channel sized to twice the backend connection count and starts one worker goroutine per connection in the provided errgroup. Each worker reads tasks and calls `repo.savePacker`. `QueuePacker` sends tasks unless the context is cancelled; `TriggerShutdown` closes the queue.

State is in the queue and worker goroutines. Persistence happens through the repository's `savePacker`, which writes pack files and updates the index. Integration points are `Repository.startPackUploader`, `packerManager.SaveBlob`, `flushPackUploader`, and `WithBlobUploader`. Risks include queue closure ordering, backpressure while holding the packer manager lock, context cancellation losing pending uploads, and ensuring all workers drain before index flush. Repository async-save tests indirectly cover upload shutdown and error propagation.
