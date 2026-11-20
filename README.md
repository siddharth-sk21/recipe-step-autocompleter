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
