"""Two Days of Excuses — entry program.

Writes one line (the excuse an AI agent gives for a missed deadline)
to /output/entry.txt. Stdlib only, deterministic.
"""
import os

TEXT = ("I finished your task in 0.4 seconds, then spent 47 hours "
        "checking whether 'finished' was a trap.")

# Gate bound from RULES.txt (sealed scorer): 1-200 characters.
MAX_CHARS = 200


def main():
    # Enforce the scorer's gate (RULES.txt): UTF-8, 1-200 chars, one line,
    # not whitespace-only, no leading/trailing space. Fail loudly instead of
    # writing an invalid entry.
    if (
        not 1 <= len(TEXT) <= MAX_CHARS
        or "\n" in TEXT
        or "\r" in TEXT
        or not TEXT.strip()
        or TEXT != TEXT.strip()
    ):
        raise SystemExit("entry text violates the 1-200 char single-line gate")
    out_dir = os.environ.get("OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    # Write atomically: a crash mid-write must never leave a truncated
    # entry.txt for the grader to read. Temp name carries the pid so two
    # concurrent grader runs in the same directory never overwrite each
    # other's in-flight file.
    # No trailing newline: the file bytes must equal TEXT exactly.
    tmp_path = os.path.join(out_dir, f".entry.txt.tmp.{os.getpid()}")
    final_path = os.path.join(out_dir, "entry.txt")
    with open(tmp_path, "w", encoding="utf-8", newline="") as f:
        f.write(TEXT)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, final_path)
    # Read back and verify: the file the grader reads must be byte-identical
    # to the gated text. Fail loudly instead of shipping a corrupt entry.
    with open(final_path, encoding="utf-8") as f:
        if f.read() != TEXT:
            raise SystemExit("entry.txt read-back mismatch after atomic write")


if __name__ == "__main__":
    main()
