# sources/storage-engines/badger/.github/workflows/ci-dgraph-tests.yml

Purpose: integration CI that tests Badger main against Dgraph main.

Important flow: on pushes to Badger `main`, it checks out `dgraph-io/dgraph`, sets up Go from Dgraph's `go.mod`, installs `gotestsum`, runs `go get github.com/dgraph-io/badger/v4@main`, sets up Node, installs protobuf compiler, regenerates Dgraph protos and checks for clean diff, builds a Dgraph Docker image, builds the Dgraph test binary, cleans test cache/containers, and runs selected Dgraph packages.

State and persistence: outputs are CI logs, Docker images/containers, regenerated files checked by diff, and test binaries. Dependencies include Dgraph repository structure, Go, Node, protobuf, Docker, and Badger module resolution. Risks: `node-version: 16 || 22` is suspicious syntax for `setup-node`, external Dgraph main instability can break Badger CI, and Docker build cost is high. Test signals are Dgraph package tests, proto diff cleanliness, and module resolution to Badger main.
