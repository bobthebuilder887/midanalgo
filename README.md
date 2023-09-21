# Midan's Sheet Algo
![Tests](https://github.com/bobthebuilder887/midanalgo/actions/workflows/main.yml/badge.svg?event=push)

## Setup
In your environment (e.g. Anaconda or virtualenv):

```{code-block} bash
git clone https://github.com/bobthebuilder887/midanalgo
cd midanalgo
python -m pip install .
```

## Run
```{code-block} bash
divide_work -t tests/sample_data.xlsx -b tests/sample_tablebase.xlsx -o output.xlsx
```

## Dev-mode
```{code-block} bash
python -m pip install -e '.[dev]'
```
