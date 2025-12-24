# data-app-template
template for future data projects

## Rust workspace support

- **Toolchain pinning**: `rust-toolchain.toml` locks the channel to stable and keeps `rustfmt`/`clippy` available so editor tooling is always consistent.
- **Shared workspace**: the root `Cargo.toml` designates `rust/data-app` as the default member and keeps a single `Cargo.lock`, which makes multi-crate changes atomic.
- **Faster builds**: `.cargo/config.toml` reuses `target/rust`, enables incremental builds, and lifts developer `codegen-units`, while Linux builds pass `-fuse-ld=mold` for quicker linking; install `mold` plus a compatible linker (e.g. `cc`) before enabling it in your environment.
- **Profiles tuned for iteration & CI releases**: dev builds keep overflow checks on with high parallelism, release builds use thin-LTO/panic-abort defaults to keep iteration fast without sacrificing correctness.
- **Getting started**: run `cargo run -p data_app` from the repo root to exercise the template; add additional members under `rust/` and the workspace `members` array as needed.
