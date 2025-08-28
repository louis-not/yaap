# YAAP

yet another ai program. because we needed another one.

## what it does

- chat with ai in terminal (interactive mode)
- ask one question and get answer (direct mode) 
- streams responses so you don't wait forever
- keeps conversation history during session
- works with openai api

## usage

interactive mode:
```bash
python src/main.py
```

direct query:
```bash
python src/main.py "what is the meaning of life"
python src/main.py hello there
```

debug mode if things break:
```bash
python src/main.py --debug
```

## setup

1. install stuff: `pip install -r requirements.txt`
2. set your openai api key somewhere
3. run it

## commands in interactive mode

- `exit` or `quit` - leaves
- `help` - shows commands
- anything else - sends to ai

that's it. it's not complicated.