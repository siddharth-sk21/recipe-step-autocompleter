# Recipe Step Autocompleter

[![Built with askThili](https://ask.thili.ai/api/v1/public/projects/tsycmws65j/badge.svg)](https://ask.thili.ai/b/tsycmws65j)

A command-line application that completes partial cooking instructions using a trained n-gram language model. It can rank probable next words, generate a continuation, or let you choose words one step at a time.

## Features

- Cleans and tokenizes a built-in recipe corpus
- Counts unigram, bigram, and trigram transitions
- Uses add-alpha smoothing for unseen words and contexts
- Falls back from trigrams to shorter n-grams
- Supports deterministic and seeded sampled generation
- Provides next-word suggestions, full continuations, and interactive completion
- Includes automated tests for preprocessing, probabilities, generation, and CLI behavior

## Milestone Status

- [x] **1. Compile a cooking-recipe corpus**
- [x] **2. Count n-grams and calculate smoothed probabilities**
- [x] **3. Generate recipe-step continuations**
- [x] **4. Build the command-line interface**

## Requirements

- Python 3.12
- Git
- Windows, macOS, or Linux
- No external model or API is required for n-gram commands

The optional files in `app/llm.py` provide settings for an external LLM integration. The current `suggest`, `generate`, and `complete` commands work entirely with the local recipe corpus.

## Windows Setup

Open PowerShell and run:

```powershell
cd D:\recipe-step-autocompleter
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Verify the installation:

```powershell
python -m app.cli hello
python -m pytest -q
```

If PowerShell blocks virtual-environment activation, allow scripts only for the current process:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Optional `.env` Setup

An `.env` file is only needed for the optional LLM helper:

```powershell
Copy-Item .env.example .env
```

Edit `.env` locally, but never commit API keys or secrets. `.env` is ignored by Git.

## macOS or Linux Setup

```bash
cd /path/to/recipe-step-autocompleter
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m app.cli hello
python -m pytest -q
```

## Using the CLI

Check that the CLI is available:

```powershell
python -m app.cli --help
```

### Suggest Next Words

```powershell
python -m app.cli suggest "add the" --count 5
```

Example:

```text
eggs        0.0156
onions      0.0156
stock       0.0156
```

The second column is the smoothed probability of each candidate word.

### Generate a Continuation

Generate deterministically by choosing the highest-probability next word:

```powershell
python -m app.cli generate "stir in" --count 10
```

Generate with probability-based sampling:

```powershell
python -m app.cli generate "add the" --count 10 --sample --seed 42
```

`--seed` makes sampled output reproducible.

### Complete a Step Interactively

Use the terminal to choose a suggested word in each round:

```powershell
python -m app.cli complete "add the" --count 5 --steps 3
```

For automated testing or a repeatable demo, choose a suggestion number automatically:

```powershell
python -m app.cli complete "add the" --count 5 --steps 3 --choose 1
```

## How It Works

1. `app/core.py` normalizes each recipe instruction into lowercase tokens.
2. The `NGramModel` counts transitions from one, two, or three preceding words.
3. Add-alpha smoothing assigns positive probabilities to unseen candidates.
4. When a full context has no observations, the model backs off to a shorter context.
5. `suggest` ranks candidates, while `generate` appends words until it reaches the word limit or an end marker.
6. `app/cli.py` exposes `hello`, `suggest`, `generate`, and `complete`.

## Project Structure

```text
app/
  core.py       Corpus preparation, n-gram model, and generation
  cli.py        Command-line commands
  llm.py        Optional external LLM helper
  storage.py    Local JSON key-value storage helper
tests/
  test_core.py  Model and milestone tests
  test_smoke.py CLI and plumbing tests
.env.example    Optional local settings template
requirements.txt
pytest.ini
README.md
```

## Running the Tests

Run the complete test suite:

```powershell
python -m pytest -q
```

A passing result ends with:

```text
20 passed
```

Run only the core model tests:

```powershell
python -m pytest tests/test_core.py -q
```

## Results and Evaluation

### Methodology

The built-in corpus currently contains 37 instructions. Evaluation uses a fixed random seed of `42` and an 80/20 instruction-level split:

- Training instructions: 29
- Held-out test instructions: 8
- Test next-word examples: 61
- Smoothing: add-alpha with `alpha = 1.0`
- Reproducibility: fixed split seed and fixed corpus

No held-out instruction is included in training. Models use the same training and test split, and top-k metrics count the true next word among the highest-ranked training-vocabulary candidates. Perplexity is calculated as `exp(mean negative log probability)` over held-out `(context, next word)` examples, including the `</s>` end marker.

Run the evaluation locally:

```powershell
python -m app.evaluation
```

This writes:

- [results/evaluation.csv](results/evaluation.csv)
- [results/evaluation.json](results/evaluation.json)

### Measured Model Comparison

| Model | Top-1 accuracy | Top-5 accuracy | Perplexity | Test examples |
|---|---:|---:|---:|---:|
| Unigram | 14.75% | 36.07% | 79.24 | 61 |
| Bigram | 16.39% | 36.07% | 70.13 | 61 |
| Trigram | 16.39% | 36.07% | 71.19 | 61 |

The bigram model has the lowest perplexity and is therefore the strongest simple model on this held-out split. The bigram and trigram models tie for top-1 accuracy and top-5 accuracy. Trigram perplexity is slightly worse than bigram perplexity because the corpus is small and longer contexts are frequently unseen, so the trigram implementation backs off more often.

Compared with the unigram baseline, the bigram model improves top-1 accuracy from 14.75% to 16.39% and reduces perplexity from 79.24 to 70.13. This demonstrates that neighboring-word context provides useful predictive information, while the small corpus prevents a large performance gap.

### Representative CLI Results

Next-word suggestions:

```text
eggs        0.0156
onions      0.0156
stock       0.0156
350         0.0078
a           0.0078
```

Greedy generation:

```text
stir in the garlic and cook until soft
```

Seeded sampling:

```text
add the pot a directions cool sauce reduce through boil hours a
```

Interactive completion:

```text
Current step: add the
1. eggs (0.0156)
2. onions (0.0156)
3. stock (0.0156)
Current step: add the eggs
1. and (0.0157)
2. with (0.0157)
3. 350 (0.0079)
Final step: add the eggs and
```

Commands used:

```powershell
python -m app.cli suggest "add the" --count 5
python -m app.cli generate "stir in" --count 10
python -m app.cli generate "add the" --count 10 --sample --seed 42
python -m app.cli complete "add the" --count 3 --steps 2 --choose 1
```

### Evaluation Limitations

- The corpus is a small demonstration set of 37 instructions, not a representative recipe dataset.
- The held-out test set contains only eight instructions and 61 next-word decisions.
- Repeated patterns and common words dominate the metrics.
- A stronger trigram result would require substantially more and more varied recipe instructions.
- Seeded sampling can produce less coherent output than greedy generation because it samples from smoothed probabilities.
- The end result is therefore a reproducible educational comparison, not a production recipe-language benchmark.

## Troubleshooting

### `python` opens a different Python version

Use the Python launcher on Windows:

```powershell
py -3.12 -m pip install -r requirements.txt
py -3.12 -m pytest -q
py -3.12 -m app.cli --help
```

### `pytest` is not recognized

Run pytest through Python to ensure it uses the active virtual environment:

```powershell
python -m pytest -q
```

### PowerShell virtual-environment activation fails

Activate only for the current shell as described in the Windows setup section. You can alternatively run the environment's executables directly:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m app.cli hello
```

### Suggestions seem repetitive or limited

The built-in corpus is intentionally small. Expand `DEFAULT_INSTRUCTIONS` in `app/core.py` with additional, diverse cooking instructions to improve output quality.

## Settings and Secrets

The optional LLM settings are stored in `.env`. This file is ignored by Git. Never commit an API key or paste a secret into source code.

If a key is exposed in GitHub, revoke it and create a replacement key before updating `.env`.

## Stretch Ideas

- Load instructions from a larger external recipe dataset
- Increase or reduce the suggestions dynamically
- Display ranked probabilities beside suggested words
- Support interactive word selection across more completion rounds
- Compare unigram, bigram, and trigram output quality
- Export generated steps to a text or JSON file
