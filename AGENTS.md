# Working on sha2

- `sha2/sha256.ri`'s asm block is written by `tools/gen_asm.py`; change
  the generator and paste its output, never the block by hand.
- Follow RustCrypto sha2's code (src/sha256/x86.rs, soft.rs) closely.
- `./check.sh` must pass on both paths; the test runs the software
  rounds too.
- Every line is at most 80 characters in documents and commit messages.
