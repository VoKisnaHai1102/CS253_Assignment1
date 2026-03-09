# Word Frequency Indexer

A fast, buffered C++ tool for building word frequency indexes from text files and querying them. Supports single-file word counts, top-K word rankings, and cross-version frequency diffs.

---

## Features

- **Buffered file reading** — configurable chunk size (256–1024 KB) for memory-efficient processing of large files
- **Case-insensitive tokenization** — normalizes all words to lowercase
- **Three query modes** — look up a word's frequency, find the top-K most frequent words, or compare word frequencies across two file versions
- **Versioned indexes** — tag each index with a version name for tracking and comparison
- **Execution timing** — reports total runtime after every run

---

## Build

```bash
g++ -std=c++17 -O2 -o analyzer main.cpp
```

---

## Usage

```
./analyzer [options]
```

### Common Options

| Flag | Description |
|------|-------------|
| `--file <path>` | Input file (for `word` and `top` queries) |
| `--file1 <path>` | First input file (for `diff` query) |
| `--file2 <path>` | Second input file (for `diff` query) |
| `--version <name>` | Version label (for `word` and `top` queries) |
| `--version1 <name>` | Version label for first file (for `diff` query) |
| `--version2 <name>` | Version label for second file (for `diff` query) |
| `--buffer <KB>` | Buffer size in KB — must be between **256** and **1024** |
| `--query <type>` | Query type: `word`, `top`, or `diff` |
| `--word <term>` | Target word (for `word` and `diff` queries) |
| `--top <K>` | Number of top words to return (for `top` query) |

---

## Query Modes

### `word` — Look up a single word's frequency

```bash
./analyzer --file verbose_logs.txt --version v1 --buffer 512 --query word --word hello
```

**Output:**
```
Allocated Buffer Size: 512 KB
Version: v1
Word Count Result: 'hello' -> 42
Total Execution Time: 0.031 seconds
```

---

### `top` — Find the K most frequent words

```bash
./analyzer --file verbose_logs.txt --version v1 --buffer 512 --query top --top 5
```

**Output:**
```
Allocated Buffer Size: 512 KB
Version: v1
Top-5 words:
the -> 1200
of -> 980
and -> 876
to -> 741
a -> 690
Total Execution Time: 0.045 seconds
```

---

### `diff` — Compare a word's frequency across two files

```bash
./analyzer --file1 verbose_logs.txt --file2 test_logs.txt --version1 v1 --version2 v2 \
               --buffer 512 --query diff --word hello
```

**Output:**
```
Allocated Buffer Size: 512 KB
Versions: v1, v2
Difference Result for 'hello':
v1: 42 | v2: 31
Difference: 11
Total Execution Time: 0.062 seconds
```

---

## Constraints & Validation

- `--buffer` must be between **256** and **1024** KB
- `--top` must be a positive integer
- All required flags must be provided for the chosen query type (the program will print a descriptive error if any are missing)

---

## Project Structure

```
.
├── main.cpp                 # Full source
├── README.md
└── ...
```

### Key Classes

| Class | Responsibility |
|-------|----------------|
| `BufferedFileReader` | Reads input files in configurable chunks, preserving word boundaries across chunks |
| `Tokenizer` | Splits text into lowercase alphanumeric tokens |
| `VersionedIndex` | Stores a word frequency map tagged with a version name |
| `WordQueryProcessor` | Executes a single-word frequency lookup |
| `TopKQueryProcessor` | Finds the top-K most frequent words using a min-heap |
| `DiffQueryProcessor` | Compares word frequencies between two versioned indexes |

---

## Requirements

- C++17 or later
- Standard library only — no external dependencies